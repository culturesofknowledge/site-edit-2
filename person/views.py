import logging
from abc import ABC
from typing import Callable, Iterable, Type, Optional, Any, NoReturn

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import F
from django.db.models.lookups import LessThanOrEqual, GreaterThanOrEqual, Exact
from django.forms import BaseForm
from django.shortcuts import render, redirect, get_object_or_404

from core import constant
from core.constant import REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_IS_RELATED_TO
from core.forms import CommentForm, ResourceForm, LocRecrefForm, PersonRecrefForm
from core.helper import renderer_utils, view_utils, query_utils, download_csv_utils, recref_utils, form_utils
from core.helper.common_recref_adapter import RecrefFormAdapter, TargetCommentRecrefAdapter, \
    TargetResourceRecrefAdapter, TargetPersonRecrefAdapter
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_utils import CommonInitFormViewTemplate, ImageHandler, BasicSearchView, FullFormHandler, \
    RecrefFormsetHandler
from core.models import Recref
from location.models import CofkUnionLocation
from person import person_utils
from person.forms import PersonForm, GeneralSearchFieldset, PersonOtherRecrefForm
from person.models import CofkUnionPerson, CofkPersonLocationMap, CofkPersonPersonMap, create_person_id, \
    CofkPersonCommentMap, CofkPersonResourceMap

log = logging.getLogger(__name__)


class PersonInitView(LoginRequiredMixin, CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'person/init_form.html', {'person_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('person:full_form', new_instance.iperson_id)

    @property
    def form_factory(self) -> Callable[..., BaseForm]:
        return PersonForm

    def on_form_changed(self, request, form) -> NoReturn:
        form.instance.person_id = create_person_id(form.instance.iperson_id)
        # KTODO handle form.instance.roles
        return super().on_form_changed(request, form)


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


class LocRecrefHandler(view_utils.MultiRecrefHandler):

    def __init__(self, request_data, model_list, name=None):
        def _find_rec_name_by_id(target_id) -> Optional[str]:
            loc = CofkUnionLocation.objects.get(location_id=target_id)
            return loc and loc.location_name

        initial_list = (m.__dict__ for m in model_list)
        initial_list = (recref_utils.convert_to_recref_form_dict(r, 'location_id', _find_rec_name_by_id)
                        for r in initial_list)

        name = name or 'loc'
        super().__init__(request_data, name=name, initial_list=initial_list,
                         recref_form_class=LocRecrefForm)

    @property
    def recref_class(self) -> Type[models.Model]:
        return CofkPersonLocationMap

    def create_recref_by_new_form(self, target_id, parent_instance) -> Optional[models.Model]:
        ps_loc: CofkPersonLocationMap = CofkPersonLocationMap()
        ps_loc.location = CofkUnionLocation.objects.get(location_id=target_id)
        if not ps_loc.location:
            # KTODO can we put it to validate function?
            log.warning(f"location_id not found -- {target_id} ")
            return None

        ps_loc.person = parent_instance
        ps_loc.relationship_type = 'was_in_location'  # KTODO support other type
        return ps_loc


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
        # KTODO handle self.person.roles, roles_titles
        self.person_form = PersonForm(request_data or None, instance=self.person)
        self.person_form.base_fields['organisation_type'].reload_choices()

        self.loc_handler = LocRecrefHandler(
            request_data, model_list=self.person.cofkpersonlocationmap_set.iterator(), )

        self.org_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='organisation',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_MEMBER_OF,
        )
        self.member_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='member',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_MEMBER_OF,
        )
        self.parent_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='parent',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_PARENT_OF,
        )
        self.children_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='children',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_PARENT_OF,
        )
        self.employer_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='employer',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_EMPLOYED,
        )
        self.employee_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='employee',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_EMPLOYED,
        )

        self.teacher_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='teacher',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_TAUGHT,
        )
        self.student_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='student',
            recref_adapter=PassivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_TAUGHT,
        )

        self.patron_handler = view_utils.MultiRecrefAdapterHandler(
            request_data, name='patron',
            recref_adapter=ActivePersonRecrefAdapter(self.person),
            recref_form_class=PersonRecrefForm,
            rel_type=constant.REL_TYPE_WAS_PATRON_OF,
        )
        self.protege_handler = view_utils.MultiRecrefAdapterHandler(
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
            prefix='res',
            request_data=request_data,
            form=ResourceForm,
            rel_type=REL_TYPE_IS_RELATED_TO,
            parent=self.person,
        ))
        self.img_handler = ImageHandler(request_data, request and request.FILES, self.person.images)

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
        fhandler.img_handler.save(request)
        form_utils.save_multi_rel_recref_formset(fhandler.person_other_formset, fhandler.person_form.instance, request)
        recref_utils.create_recref_if_field_exist(fhandler.person_form,
                                                  fhandler.person_form.instance,
                                                  request.user.username,
                                                  selected_id_field_name='selected_other_id',
                                                  rel_type=constant.REL_TYPE_UNSPECIFIED_RELATIONSHIP_WITH,
                                                  recref_adapter=PersonOtherRecrefForm.create_recref_adapter())

        # KTODO save birthplace, deathplace
        # KTODo save roles_titles

        # reload all form data for rendering
        fhandler.load_data(iperson_id, request_data=None)

    return fhandler.render_form(request)


class PersonSearchView(LoginRequiredMixin, BasicSearchView):

    @property
    def entity(self) -> str:
        return 'person,people'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    @property
    def merge_page_vname(self) -> str:
        return 'person:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'person:return_quick_init'

    def get_queryset(self):
        field_fn_maps = {
            'gender': lambda f, v: Exact(F(f), '' if v == 'U' else v),
            'person_or_group': lambda _, v: Exact(F('is_organisation'), 'Y' if v == 'G' else ''),
            'birth_year_from': lambda _, v: GreaterThanOrEqual(F('date_of_birth_year'), v),
            'birth_year_to': lambda _, v: LessThanOrEqual(F('date_of_birth_year'), v),
            'death_year_from': lambda _, v: GreaterThanOrEqual(F('date_of_death_year'), v),
            'death_year_to': lambda _, v: LessThanOrEqual(F('date_of_death_year'), v),
            'flourished_year_from': lambda _, v: GreaterThanOrEqual(F('flourished_of_death_year'), v),
            'flourished_year_to': lambda _, v: LessThanOrEqual(F('flourished_of_death_year'), v),
            'change_timestamp_from': lambda _, v: GreaterThanOrEqual(F('change_timestamp'), v),
            'change_timestamp_to': lambda _, v: LessThanOrEqual(F('change_timestamp'), v),
        }

        queryset = CofkUnionPerson.objects.all()

        queries = query_utils.create_queries_by_field_fn_maps(field_fn_maps, self.request_data)
        queries.extend(
            query_utils.create_queries_by_lookup_field(self.request_data, [
                'foaf_name', 'iperson_id', 'editors_notes',
                'further_reading', 'change_user'
            ])
        )

        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('person/search_table_layout.html')

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return renderer_utils.create_compact_renderer(item_template_name='person/compact_item.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        default_values = {
            'foaf_name_lookup': 'starts_with',
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


class PersonCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonCommentMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonCommentMap
        recref.person = parent
        recref.comment = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersoncommentmap_set, rel_type)


class PersonResourceFormsetHandler(RecrefFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return PersonResourceRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkPersonResourceMap.objects.filter(person=parent, resource=target).first()


class PersonResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonResourceMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonResourceMap
        recref.person = parent
        recref.resource = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonresourcemap_set, rel_type)


class PersonPersonRecrefAdapter(TargetPersonRecrefAdapter, ABC):
    def __init__(self, parent=None):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonPersonMap


class ActivePersonRecrefAdapter(PersonPersonRecrefAdapter):

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonPersonMap
        recref.person = parent
        recref.related = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.active_relationships, rel_type)

    def target_id_name(self):
        return 'related_id'


class PassivePersonRecrefAdapter(PersonPersonRecrefAdapter):

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonPersonMap
        recref.person = target
        recref.related = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.passive_relationships, rel_type)

    def target_id_name(self):
        return 'person_id'
