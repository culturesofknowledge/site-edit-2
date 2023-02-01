import logging
from typing import Callable, Iterable, Type, Any, NoReturn, TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import F, Count, Q
from django.db.models.lookups import LessThanOrEqual, GreaterThanOrEqual, Exact
from django.forms import BaseForm
from django.shortcuts import render, redirect, get_object_or_404

from core import constant
from core.constant import REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_WAS_BORN_IN_LOCATION, REL_TYPE_DIED_AT_LOCATION, \
    REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_CREATED, REL_TYPE_SENT, REL_TYPE_SIGNED, REL_TYPE_MENTION, TRUE_CHAR
from core.forms import CommentForm, PersonRecrefForm
from core.helper import renderer_utils, view_utils, query_utils, download_csv_utils, recref_utils, form_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.date_utils import str_to_std_datetime
from core.helper.model_utils import ModelLike
from core.helper.recref_handler import RecrefFormsetHandler, RoleCategoryHandler, ImageRecrefHandler, \
    TargetResourceFormsetHandler, MultiRecrefAdapterHandler, SingleRecrefHandler
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_handler import FullFormHandler
from core.helper.view_utils import CommonInitFormViewTemplate, BasicSearchView, MergeChoiceViews, MergeActionViews
from core.models import Recref
from person import person_utils
from person.forms import PersonForm, GeneralSearchFieldset, PersonOtherRecrefForm, field_label_map, \
    search_gender_choices, search_person_or_group
from person.models import CofkUnionPerson, CofkPersonPersonMap, create_person_id, \
    CofkPersonCommentMap, CofkPersonResourceMap, CofkPersonImageMap
from person.recref_adapter import PersonCommentRecrefAdapter, PersonResourceRecrefAdapter, PersonRoleRecrefAdapter, \
    ActivePersonRecrefAdapter, PassivePersonRecrefAdapter, PersonImageRecrefAdapter, PersonLocRecrefAdapter
from person.view_components import PersonFormDescriptor

if TYPE_CHECKING:
    from core.helper.view_utils import MergeChoiceContext

log = logging.getLogger(__name__)


def create_context_is_org_form(is_organisation: str):
    return {
        'is_org_form': is_organisation == TRUE_CHAR,
    }


class PersonInitView(LoginRequiredMixin, CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'person/init_form.html', {
            'person_form': form
        } | create_context_is_org_form(form.initial.get('is_organisation')))

    def resp_after_saved(self, request, form, new_instance):
        return redirect('person:full_form', new_instance.iperson_id)

    @property
    def form_factory(self) -> Callable[..., BaseForm]:
        return PersonForm

    def on_form_changed(self, request, form) -> NoReturn:
        form.instance.person_id = create_person_id(form.instance.iperson_id)
        return super().on_form_changed(request, form)

    def get(self, request, *args, **kwargs):
        is_org_form = request and request.GET.get('person_form_type') == 'org'
        if is_org_form:
            initial = {'is_organisation': TRUE_CHAR, }
        else:
            initial = {}

        form = self.form_factory(initial=initial)
        return self.resp_form_page(request, form)


class PersonQuickInitView(PersonInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('person:return_quick_init', new_instance.iperson_id)


@login_required
def return_quick_init(request, pk):
    person = CofkUnionPerson.objects.get(iperson_id=pk)
    return view_utils.render_return_quick_init(
        request, 'Person',
        person_utils.get_recref_display_name(person),
        person_utils.get_recref_target_id(person),
    )


class OrganisationRecrefConvertor:

    @property
    def target_id_name(self):
        return 'location_id'


def _get_other_persons_by_type(person: CofkUnionPerson, person_type: str) -> Iterable[CofkPersonPersonMap]:
    persons = (p for p in person.active_relationships.iterator()
               if p.person_type == person_type)
    return persons


class PersonFFH(FullFormHandler):

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        self.person = get_object_or_404(CofkUnionPerson, iperson_id=pk)

        self.birth_loc_handler = SingleRecrefHandler(
            form_field_name='birth_place',
            rel_type=REL_TYPE_WAS_BORN_IN_LOCATION,
            create_recref_adapter_fn=PersonLocRecrefAdapter,
        )
        self.death_loc_handler = SingleRecrefHandler(
            form_field_name='death_place',
            rel_type=REL_TYPE_DIED_AT_LOCATION,
            create_recref_adapter_fn=PersonLocRecrefAdapter,
        )

        initial_dict = (
                {}
                | self.birth_loc_handler.create_init_dict(self.person)
                | self.death_loc_handler.create_init_dict(self.person)
        )
        self.person_form = PersonForm(request_data or None, instance=self.person, initial=initial_dict)
        self.person_form.base_fields['organisation_type'].reload_choices()

        self.org_handler = MultiRecrefAdapterHandler(
            request_data, name='organisation',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_MEMBER_OF,
        )
        self.member_handler = MultiRecrefAdapterHandler(
            request_data, name='member',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_MEMBER_OF,
        )
        self.parent_handler = MultiRecrefAdapterHandler(
            request_data, name='parent',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_PARENT_OF,
        )
        self.children_handler = MultiRecrefAdapterHandler(
            request_data, name='children',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_PARENT_OF,
        )
        self.employer_handler = MultiRecrefAdapterHandler(
            request_data, name='employer',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_EMPLOYED,
        )
        self.employee_handler = MultiRecrefAdapterHandler(
            request_data, name='employee',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_EMPLOYED,
        )

        self.teacher_handler = MultiRecrefAdapterHandler(
            request_data, name='teacher',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_TAUGHT,
        )
        self.student_handler = MultiRecrefAdapterHandler(
            request_data, name='student',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_TAUGHT,
        )

        self.patron_handler = MultiRecrefAdapterHandler(
            request_data, name='patron',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_WAS_PATRON_OF,
        )
        self.protege_handler = MultiRecrefAdapterHandler(
            request_data, name='protege',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_WAS_PATRON_OF,
        )
        self.person_other_formset = PersonOtherRecrefForm.create_formset_by_records(
            request_data,
            self.person.active_relationships.iterator() if self.person else [],
            prefix='person_other'
        )

        self.add_recref_formset_handler(PersonCommentFormsetHandler(
            prefix='comment',
            request_data=request_data,
            form=CommentForm,
            rel_type=REL_TYPE_COMMENT_REFERS_TO,
            parent=self.person,
        ))

        self.add_recref_formset_handler(PersonResourceFormsetHandler(
            request_data=request_data,
            parent=self.person,
        ))
        self.img_recref_handler = PersonImageRecrefHandler(request_data, request and request.FILES,
                                                           parent=self.person)

        self.role_handler = RoleCategoryHandler(PersonRoleRecrefAdapter(self.person))

        self.other_loc_handler = MultiRecrefAdapterHandler(
            request_data, name='other_loc',
            recref_adapter=PersonLocRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_WAS_IN_LOCATION,
        )

    def create_context(self):
        context = super().create_context()
        context.update(
            self.role_handler.create_context()
            | PersonFormDescriptor(self.person).create_context()
            | create_context_is_org_form(self.person.is_organisation)
        )
        return context

    def render_form(self, request):
        return render(request, 'person/full_form.html', self.create_context())


@login_required
def full_form(request, iperson_id):
    fhandler = PersonFFH(iperson_id, request_data=request.POST, request=request)

    # handle form submit
    if request.POST:

        # ----- validate
        if fhandler.is_invalid():
            return fhandler.render_form(request)

        # ------- save
        fhandler.maintain_all_recref_records(request, fhandler.person_form.instance)

        fhandler.person_form.save()
        fhandler.save_all_recref_formset(fhandler.person, request)
        fhandler.img_recref_handler.save(fhandler.person_form.instance, request)
        form_utils.save_multi_rel_recref_formset(fhandler.person_other_formset, fhandler.person_form.instance, request)
        recref_utils.create_recref_if_field_exist(fhandler.person_form,
                                                  fhandler.person_form.instance,
                                                  request.user.username,
                                                  selected_id_field_name='selected_other_id',
                                                  rel_type=constant.REL_TYPE_UNSPECIFIED_RELATIONSHIP_WITH,
                                                  recref_adapter=PersonOtherRecrefForm.create_recref_adapter())
        fhandler.role_handler.save(request, fhandler.person_form.instance)

        fhandler.birth_loc_handler.upsert_recref_if_field_exist(
            fhandler.person_form, fhandler.person_form.instance,
            request.user.username
        )
        fhandler.death_loc_handler.upsert_recref_if_field_exist(
            fhandler.person_form, fhandler.person_form.instance,
            request.user.username
        )

        # reload all form data for rendering
        fhandler.load_data(iperson_id, request_data=None)

    return fhandler.render_form(request)


class PersonSearchView(LoginRequiredMixin, BasicSearchView):

    @property
    def entity(self) -> str:
        return 'person,people'

    @property
    def search_fields(self) -> list[str]:
        return ['foaf_name', 'iperson_id', 'editors_notes', 'sent', 'recd', 'all_works', 'mentioned',
                'further_reading', 'other_details', 'images', 'change_user']

    @property
    def search_field_label_map(self) -> dict:
        return field_label_map

    @property
    def search_field_fn_maps(self) -> dict:
        return {'gender': lambda f, v: Exact(F(f), '' if v == 'U' else v),
                'person_or_group': lambda _, v: Exact(F('is_organisation'), 'Y' if v == 'G' else ''),
                'birth_year_from': lambda _, v: GreaterThanOrEqual(F('date_of_birth_year'), v),
                'birth_year_to': lambda _, v: LessThanOrEqual(F('date_of_birth_year'), v),
                'death_year_from': lambda _, v: GreaterThanOrEqual(F('date_of_death_year'), v),
                'death_year_to': lambda _, v: LessThanOrEqual(F('date_of_death_year'), v),
                'flourished_year_from': lambda _, v: GreaterThanOrEqual(F('flourished_year'), v),
                'flourished_year_to': lambda _, v: LessThanOrEqual(F('flourished2_year'), v),
                } | query_utils.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                     'change_timestamp', str_to_std_datetime)

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('foaf_name', 'Name',),  # TODO this is in a view cofk_union_person_view
            ('date_of_birth', 'Born',),
            ('date_of_death', 'Died',),
            ('flourished', 'Flourished',),
            ('gender', 'Gender',),
            ('is_organisation', 'Person or group?',),
            ('org_type', 'Type of group',),
            ('sent', 'Sent',),
            ('recd', 'Rec\'d',),
            ('all_works', 'Sent or Rec\'d',),
            ('mentioned', 'Mentioned',),
            ('editors_notes', 'Editors\' notes',),
            ('further_reading', 'Further reading',),
            ('images', 'Images',),
            ('other_details_summary', 'Other details',),
            ('other_details_summary_searchable', 'Other details',),
            ('change_timestamp', 'Change Timestamp',),
            ('change_user', 'Change user',),
            ('iperson_id', 'Person or Group ID',),
        ]

    @property
    def merge_page_vname(self) -> str:
        return 'person:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'person:return_quick_init'

    @property
    def simplified_query(self) -> list[str]:
        simplified_query = super().simplified_query

        if self.search_field_fn_maps:
            gender = self.request_data['gender'] if 'gender' in self.request_data else None
            person_or_group = self.request_data['person_or_group'] if 'person_or_group' in self.request_data else None

            if gender:
                gender = [g[1].lower() for g in search_gender_choices if g[0] == gender][0]
                simplified_query.append(f'Of {gender} gender.')

            if person_or_group:
                person_or_group = [pog[1].lower() for pog in search_person_or_group if pog[0] == person_or_group][0]
                simplified_query.append(f'Is a {person_or_group}.')

            for _range in [('birth_year_from', 'birth_year_to', 'Born'),
                           ('death_year_from', 'death_year_to', 'Died'),
                           ('flourished_year_from', 'flourished_year_to', 'Flourished')]:
                _from = self.request_data[_range[0]] if _range[0] in self.request_data else None
                _to = self.request_data[_range[1]] if _range[1] in self.request_data else None

                if _to and _from:
                    simplified_query.append(f'{_range[2]} between {_from} and {_to}.')
                elif _to:
                    simplified_query.append(f'{_range[2]} before {_to}.')
                elif _from:
                    simplified_query.append(f'{_range[2]} after {_from}.')

        return simplified_query

    def create_queryset_by_queries(self, model_class: Type[models.Model], queries: Iterable[Q]):
        queryset = model_class.objects.all()

        annotate = {'sent': Count('works',
                                  filter=Q(cofkworkpersonmap__relationship_type__in=[REL_TYPE_CREATED, REL_TYPE_SENT,
                                                                                     REL_TYPE_SIGNED])),
                    'recd': Count('works', filter=Q(cofkworkpersonmap__relationship_type=REL_TYPE_WAS_ADDRESSED_TO)),
                    'mentioned': Count('works', filter=Q(cofkworkpersonmap__relationship_type=REL_TYPE_MENTION))
                    }

        annotate['all_works'] = annotate['sent'] + annotate['recd']

        queryset = queryset.annotate(**annotate)

        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_queryset(self):
        queries = query_utils.create_queries_by_field_fn_maps(self.search_field_fn_maps, self.request_data)

        search_fields_maps = {'foaf_name': ['foaf_name', 'skos_altlabel', 'person_aliases', 'skos_hiddenlabel',],
                                            #'summary__other_details_summary_searchable'],
                              'images': ['images__image_filename'],
                              'other_details': ['summary__other_details_summary_searchable']}

        queries.extend(
            query_utils.create_queries_by_lookup_field(self.request_data, self.search_fields, search_fields_maps)
        )

        return self.create_queryset_by_queries(CofkUnionPerson, queries).distinct()

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('person/search_table_layout.html')

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return renderer_utils.create_compact_renderer(item_template_name='person/compact_item.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        default_values = {
            # 'foaf_name_lookup': 'starts_with',
        }
        request_data = default_values | self.request_data.dict()

        return [GeneralSearchFieldset(request_data)]

    @property
    def download_csv_handler(self) -> DownloadCsvHandler:
        return PersonDownloadCsvHandler()


class PersonDownloadCsvHandler(DownloadCsvHandler):
    def get_header_list(self) -> list[str]:
        return [
            "ID",
            "Name",
            "Born",
            "Died",
            "Flourished",
            "Org?",
            "Type of group",
            "Sent",
            "Recd",
            "All works",
            "Researchers notes",
            "Related resources",
            "Mentioned",
            "Editor's notes",
            "Further reading",
            "Images",
            "Change user",
            "Change timestamp",
        ]

    @staticmethod
    def to_date_str(year, month, day) -> str:
        if year and not month and not day:
            return str(year)

        return f'{year}-{month}-{day}'

    def obj_to_values(self, obj) -> Iterable[Any]:
        obj: CofkUnionPerson
        org_type = obj.organisation_type
        org_type = org_type.org_type_desc if org_type else ''
        values = [
            obj.iperson_id,
            obj.foaf_name,
            self.to_date_str(obj.date_of_birth_year, obj.date_of_birth_month, obj.date_of_birth_day),
            self.to_date_str(obj.date_of_death_year, obj.date_of_death_month, obj.date_of_death_day),
            self.to_date_str(obj.flourished_year, obj.flourished_month, obj.flourished_day),
            obj.is_organisation,
            org_type,
            '0',  # KTODO send value
            '0',  # KTODO recd value
            '0',  # KTODO All works, should be send + recd
            download_csv_utils.join_comment_lines(obj.comments.iterator()),
            download_csv_utils.join_resource_lines(obj.resources.iterator()),
            '',  # KTODO mentioned
            obj.editors_notes,
            obj.further_reading,
            download_csv_utils.join_image_lines(obj.images.iterator()),
            obj.change_timestamp,
            obj.change_user,
        ]
        return values


class PersonCommentFormsetHandler(RecrefFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return PersonCommentRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkPersonCommentMap.objects.filter(person=parent, comment=target).first()


class PersonResourceFormsetHandler(TargetResourceFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return PersonResourceRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkPersonResourceMap.objects.filter(person=parent, resource=target).first()


class PersonImageRecrefHandler(ImageRecrefHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return PersonImageRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkPersonImageMap.objects.filter(person=parent, image=target).first()


class PersonMergeChoiceView(LoginRequiredMixin, MergeChoiceViews):
    @property
    def action_vname(self):
        return 'person:merge_action'

    def to_context_list(self, merge_id_list: list[str]) -> Iterable['MergeChoiceContext']:
        return self.create_merge_choice_context_by_id_field(CofkUnionPerson.iperson_id, merge_id_list)


class PersonMergeActionView(LoginRequiredMixin, MergeActionViews):
    @property
    def return_vname(self) -> str:
        return 'person:search'

    @property
    def target_model_class(self) -> Type[ModelLike]:
        return CofkUnionPerson
