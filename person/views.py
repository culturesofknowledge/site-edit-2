import logging
from typing import List, Tuple, Callable, Iterable, Type, Optional, Any, NoReturn

from django.db import models
from django.forms import BaseForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from core.helper import renderer_utils, view_utils
from core.helper.view_utils import DefaultSearchView, CommonInitFormViewTemplate
from location.models import CofkUnionLocation
from person.forms import PersonForm
from person.models import CofkUnionPerson, CofkPersonLocationMap, CofkPersonPersonMap

log = logging.getLogger(__name__)


class PersonInitView(CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'person/init_form.html', {'person_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('person:full_form', new_instance.iperson_id)

    @property
    def form_factory(self) -> Callable[..., BaseForm]:
        return PersonForm

    def on_form_changed(self, request, form) -> NoReturn:
        form.instance.person_id = f'cofk_union_person-iperson_id:{form.instance.iperson_id}'
        return super().on_form_changed(request, form)


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

    def __init__(self, request_data, model_list, name=None):
        def _find_rec_name_by_id(target_id) -> Optional[str]:
            loc = CofkUnionLocation.objects.get(location_id=target_id)
            return loc and loc.location_name

        initial_list = (m.__dict__ for m in model_list)
        initial_list = (convert_to_recref_form_dict(r, 'location_id', _find_rec_name_by_id)
                        for r in initial_list)

        name = name or 'loc'
        super().__init__(request_data, name=name, initial_list=initial_list)

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


class PersonRecrefHandler(view_utils.MultiRecrefHandler):

    def __init__(self, request_data, person_type: str, model_list=None, name=None):
        def _find_rec_name_by_id(target_id) -> Optional[str]:
            record = CofkUnionPerson.objects.get(iperson_id=target_id)
            return record and record.foaf_name

        initial_list = (m.__dict__ for m in model_list)
        initial_list = (convert_to_recref_form_dict(r, 'related_id', _find_rec_name_by_id)
                        for r in initial_list)

        name = name or 'person'
        super().__init__(request_data, name=name, initial_list=initial_list)
        self.person_type = person_type

    @property
    def recref_class(self) -> Type[models.Model]:
        return CofkPersonPersonMap

    def create_recref_by_new_form(self, target_id, new_form, parent_instance) -> Optional[models.Model]:
        recref: CofkPersonPersonMap = CofkPersonPersonMap()
        recref.related = CofkUnionPerson.objects.get(iperson_id=target_id)
        if not recref.related:
            # KTODO can we put it to validate function?
            log.warning(f"person not found -- {target_id} ")
            return None

        recref.person = parent_instance
        recref.relationship_type = 'member_of'
        recref.person_type = self.person_type
        return recref


def log_invalid(form_formset: Iterable):
    form_formset = (f for f in form_formset if not f.is_valid())
    for f in form_formset:
        log.debug(f'invalid form [{f}]')


def _get_other_persons_by_type(person: CofkUnionPerson, person_type: str) -> Iterable[CofkPersonPersonMap]:
    persons = (p for p in person.active_relationships.iterator()
               if p.person_type == person_type)
    return persons


class PersonFullFormHandler:
    def __init__(self, iperson_id, request_data, ):
        self.load_data(iperson_id, request_data=request_data)

    def load_data(self, iperson_id, request_data=None):
        self.person = get_object_or_404(CofkUnionPerson, iperson_id=iperson_id)
        self.person_form = PersonForm(request_data or None, instance=self.person)
        self.loc_handler = LocRecrefHandler(
            request_data, model_list=self.person.cofkpersonlocationmap_set.iterator(), )

        self.org_handler = PersonRecrefHandler(
            request_data,
            name='organisation',
            person_type='organisation',
            model_list=_get_other_persons_by_type(self.person, 'organisation'), )

    def render_form(self, request):
        context = (
                {
                    'person_form': self.person_form,
                }
                | self.loc_handler.create_context()
                | self.org_handler.create_context()
        )
        return render(request, 'person/full_form.html', context)


def full_form(request, iperson_id):
    fhandler = PersonFullFormHandler(iperson_id, request_data=request.POST or None)

    # handle form submit
    if request.POST:
        form_formsets = [fhandler.person_form,
                         fhandler.loc_handler.new_form, fhandler.loc_handler.update_formset,
                         fhandler.org_handler.new_form, fhandler.org_handler.update_formset,  # KTODO
                         ]
        log_invalid(form_formsets)
        if view_utils.any_invalid(form_formsets):
            return fhandler.render_form(request)
        for recref_handler in [
            fhandler.loc_handler,
            fhandler.org_handler,
        ]:
            recref_handler.maintain_record(request, fhandler.person_form.instance)

        fhandler.person_form.save()

        fhandler.load_data(iperson_id, request_data=None)

    return fhandler.render_form(request)


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
    def merge_page_vname(self) -> str:
        return 'person:merge'
    @property
    def return_quick_init_vname(self) -> str:
        return 'person:return_quick_init'

    def get_queryset(self):
        # KTODO
        queryset = CofkUnionPerson.objects.all()
        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('person/search_table_layout.html')
