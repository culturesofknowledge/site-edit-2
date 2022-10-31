import logging
import warnings
from typing import Callable, Iterable, Type, Optional, Any, NoReturn

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import F
from django.db.models.lookups import LessThanOrEqual, GreaterThanOrEqual, Exact
from django.forms import BaseForm
from django.shortcuts import render, redirect, get_object_or_404

from core.forms import CommentForm, ResourceForm, LocRecrefForm, PersonRecrefForm
from core.helper import renderer_utils, view_utils, model_utils, query_utils, download_csv_utils, recref_utils
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_utils import CommonInitFormViewTemplate, ImageHandler, BasicSearchView, FullFormHandler
from location.models import CofkUnionLocation
from person import person_utils
from person.forms import PersonForm, GeneralSearchFieldset
from person.models import CofkUnionPerson, CofkPersonLocationMap, CofkPersonPersonMap, create_person_id

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


class PersonRecrefHandler(view_utils.MultiRecrefHandler):
    # KTODO use view_utils.MultiRecrefAdapterHandler

    def __init__(self, request_data, person_type: str,
                 person: CofkUnionPerson,
                 name=None, ):
        def _find_rec_name_by_id(target_id) -> Optional[str]:
            record = CofkUnionPerson.objects.get(pk=target_id)
            return record and record.foaf_name

        initial_list = (m.__dict__ for m in _get_other_persons_by_type(person, person_type))
        initial_list = (recref_utils.convert_to_recref_form_dict(r, 'related_id', _find_rec_name_by_id)
                        for r in initial_list)

        name = name or person_type
        super().__init__(request_data, name=name, initial_list=initial_list,
                         recref_form_class=PersonRecrefForm)
        self.person_type = person_type

    @property
    def recref_class(self) -> Type[models.Model]:
        return CofkPersonPersonMap

    def create_recref_by_new_form(self, target_id, parent_instance) -> Optional[models.Model]:
        recref: CofkPersonPersonMap = CofkPersonPersonMap()
        recref.related = CofkUnionPerson.objects.get(pk=target_id)
        if not recref.related:
            # KTODO can we put it to validate function?
            log.warning(f"person not found -- {target_id} ")
            return None

        recref.person = parent_instance
        recref.relationship_type = 'member_of'
        recref.person_type = self.person_type  # KTODO should use relationship_type instance
        return recref


def _get_other_persons_by_type(person: CofkUnionPerson, person_type: str) -> Iterable[CofkPersonPersonMap]:
    persons = (p for p in person.active_relationships.iterator()
               if p.person_type == person_type)
    return persons


class PersonFullFormHandler(FullFormHandler):

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        self.person = get_object_or_404(CofkUnionPerson, iperson_id=pk)
        # KTODO handle self.person.roles, roles_titles
        self.person_form = PersonForm(request_data or None, instance=self.person)
        self.loc_handler = LocRecrefHandler(
            request_data, model_list=self.person.cofkpersonlocationmap_set.iterator(), )

        self.org_handler = PersonRecrefHandler(request_data, person_type='organisation',
                                               person=self.person)
        self.parent_handler = PersonRecrefHandler(request_data, person_type='parent',
                                                  person=self.person)
        self.children_handler = PersonRecrefHandler(request_data, person_type='children',
                                                    person=self.person)

        self.employer_handler = PersonRecrefHandler(request_data, person_type='employer',
                                                    person=self.person)
        self.employee_handler = PersonRecrefHandler(request_data, person_type='employee',
                                                    person=self.person)
        self.teacher_handler = PersonRecrefHandler(request_data, person_type='teacher',
                                                   person=self.person)
        self.student_handler = PersonRecrefHandler(request_data, person_type='student',
                                                   person=self.person)
        self.patron_handler = PersonRecrefHandler(request_data, person_type='patron',
                                                  person=self.person)
        self.protege_handler = PersonRecrefHandler(request_data, person_type='protege',
                                                   person=self.person)
        self.other_handler = PersonRecrefHandler(request_data, person_type='other',
                                                 name='person_other',
                                                 person=self.person)

        self.comment_formset = view_utils.create_formset(CommentForm, post_data=request_data,
                                                         prefix='comment',
                                                         initial_list=model_utils.related_manager_to_dict_list(
                                                             self.person.comments), )
        self.res_formset = view_utils.create_formset(ResourceForm, post_data=request_data,
                                                     prefix='res',
                                                     initial_list=model_utils.related_manager_to_dict_list(
                                                         self.person.resources), )
        self.img_handler = ImageHandler(request_data, request and request.FILES, self.person.images)

    def render_form(self, request):
        return render(request, 'person/full_form.html', self.create_context())


@login_required
def full_form(request, iperson_id):
    fhandler = PersonFullFormHandler(iperson_id, request_data=request.POST, request=request)

    # handle form submit
    if request.POST:

        # ----- validate
        if fhandler.is_invalid():
            return fhandler.render_form(request)

        # ------- save
        fhandler.maintain_all_recref_records(request, fhandler.person_form.instance)

        fhandler.person_form.save()
        view_utils.save_formset(fhandler.comment_formset, fhandler.person.comments,
                                model_id_name='comment_id')
        view_utils.save_formset(fhandler.res_formset, fhandler.person.resources,
                                model_id_name='resource_id')
        fhandler.img_handler.save(request)

        # KTODO save birthplace, deathplace
        # KTODo save roles_titles

        # reload all form data for rendering
        fhandler.load_data(iperson_id, request_data=None)

    return fhandler.render_form(request)


class PersonSearchView(LoginRequiredMixin, BasicSearchView):

    @property
    def title(self) -> str:
        return 'Person'

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
