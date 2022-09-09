import logging
from typing import List, Tuple, Callable, Iterable, Type, Optional, Any

from django.db import models
from django.forms import BaseForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from core.helper import renderer_utils, view_utils
from core.helper.view_utils import DefaultSearchView, CommonInitFormViewTemplate
from location.models import CofkUnionLocation
from person.forms import PersonForm
from person.models import CofkUnionPerson, CofkPersonLocationMap, CofkPersonOrganisationMap

log = logging.getLogger(__name__)


class PersonInitView(CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'person/init_form.html', {'person_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('person:full_form', new_instance.iperson_id)

    @property
    def form_factory(self) -> Callable[..., BaseForm]:
        return PersonForm


class PersonQuickInitView(PersonInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('person:return_quick_init', new_instance.iperson_id)


def return_quick_init(request, pk):
    person = CofkUnionPerson.objects.get(iperson_id=pk)
    return view_utils.redirect_return_quick_init(
        request, 'Person', person.foaf_name, person.iperson_id, )


def convert_to_recref_form_dict(record_dict: dict, target_id_name: str,
                                find_rec_name_by_id_fn: Callable[[Any], str]) -> dict:
    target_id = record_dict.get(target_id_name, '')
    record_dict['target_id'] = target_id
    if (rec_name := find_rec_name_by_id_fn(target_id)) is None:
        log.warning(f"[{target_id_name}] record not found -- [{target_id}]")
    else:
        record_dict['rec_name'] = rec_name

    return record_dict


class LocRecrefHandler(view_utils.MultiRecrefHandler):

    def __init__(self, request_data, model_list, name=None, **kwargs):
        def _find_rec_name_by_id(target_id) -> Optional[str]:
            loc = CofkUnionLocation.objects.get(location_id=target_id)
            return loc and loc.location_name

        initial_list = (m.__dict__ for m in model_list)
        initial_list = (convert_to_recref_form_dict(r, 'location_id', _find_rec_name_by_id)
                        for r in initial_list)

        name = name or 'loc'
        super().__init__(request_data, name=name, initial_list=initial_list, **kwargs)

    @property
    def recref_class(self) -> Type[models.Model]:
        return CofkPersonLocationMap

    def create_recref_by_new_form(self, target_id, new_form, parent_instance) -> Optional[models.Model]:
        ps_loc: CofkPersonLocationMap = CofkPersonLocationMap()
        ps_loc.location = CofkUnionLocation.objects.get(location_id=target_id)
        if not ps_loc.location:
            # KTODO can we put it to validate function?
            log.warning(f"location_id not found -- {target_id} ")
            return None

        ps_loc.person = parent_instance
        ps_loc.relationship_type = 'was_in_location'
        return ps_loc


class OrganisationRecrefConvertor:

    @property
    def target_id_name(self):
        return 'location_id'


class OrganisationRecrefHandler(view_utils.MultiRecrefHandler):

    def __init__(self, request_data, model_list, name=None, **kwargs):
        def _find_rec_name_by_id(target_id) -> Optional[str]:
            record = CofkUnionPerson.objects.get(iperson_id=target_id)
            return record and record.foaf_name

        initial_list = (m.__dict__ for m in model_list)
        initial_list = (convert_to_recref_form_dict(r, 'organisation_id', _find_rec_name_by_id)
                        for r in initial_list)

        name = name or 'org'
        super().__init__(request_data, name=name, initial_list=initial_list, **kwargs)

    @property
    def recref_class(self) -> Type[models.Model]:
        return CofkPersonOrganisationMap

    def create_recref_by_new_form(self, target_id, new_form, parent_instance) -> Optional[models.Model]:
        recref: CofkPersonOrganisationMap = CofkPersonOrganisationMap()
        recref.organisation = CofkUnionPerson.objects.get(iperson_id=target_id)
        if not recref.organisation:
            # KTODO can we put it to validate function?
            log.warning(f"person not found -- {target_id} ")
            return None

        recref.owner_person = parent_instance
        recref.relationship_type = 'member_of'
        return recref


def log_invalid(form_formset: Iterable):
    form_formset = (f for f in form_formset if not f.is_valid())
    for f in form_formset:
        log.debug(f'invalid form [{f}]')


def full_form(request, iperson_id):
    person = get_object_or_404(CofkUnionPerson, iperson_id=iperson_id)
    person_form = PersonForm(request.POST or None, instance=person)
    loc_handler = LocRecrefHandler(
        request.POST, many_related_manager=person.cofkpersonlocationmap_set, )
    org_handler = OrganisationRecrefHandler(
        request.POST, many_related_manager=person.cofkpersonorganisationmap_set, )

    def _render_full_form():
        context = (
                {
                    'person_form': person_form,
                }
                | loc_handler.create_context()
                | org_handler.create_context()
        )
        return render(request, 'person/full_form.html', context)

    if request.POST:
        form_formsets = [person_form,
                         loc_handler.new_form, loc_handler.update_formset,
                         # org_handler.new_form, org_handler.update_formset,
                         ]
        log_invalid(form_formsets)
        if view_utils.any_invalid(form_formsets):
            return _render_full_form()

        loc_handler.maintain_record(request, person_form.instance)
        org_handler.maintain_record(request, person_form.instance)

        person_form.save()

    return _render_full_form()


class PersonSearchView(DefaultSearchView):

    @property
    def title(self) -> str:
        return 'Person'

    @property
    def sort_by_choices(self) -> List[Tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    @property
    def merge_page_name(self) -> View:
        return 'person:merge'

    def get_queryset(self):
        # KTODO
        queryset = CofkUnionPerson.objects.all()
        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('person/search_table_layout.html')
