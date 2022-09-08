import logging
from typing import List, Tuple, Callable, Iterable

from django.forms import BaseForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from core.forms import RecrefForm
from core.helper import renderer_utils, view_utils
from core.helper.view_utils import DefaultSearchView, CommonInitFormViewTemplate
from location.models import CofkUnionLocation
from person.forms import PersonForm
from person.models import CofkUnionPerson, CofkPersonLocationMap

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


def _prepare_per_loc_data(form_dict: dict):
    loc_id = form_dict.get('location_id', '')
    form_dict['target_id'] = loc_id
    form_dict['recref_id'] = form_dict.get('person_location_id', '')
    loc = CofkUnionLocation.objects.get(location_id=loc_id)
    if not loc:
        log.warning(f"location not found -- [{loc_id}]")
    else:
        form_dict['rec_name'] = loc.location_name

    return form_dict


def full_form(request, iperson_id):
    person = get_object_or_404(CofkUnionPerson, iperson_id=iperson_id)
    person_form = PersonForm(request.POST or None, instance=person)
    new_loc_form = RecrefForm(request.POST or None, prefix='new_loc')

    loc_formset = view_utils.create_formset(RecrefForm, post_data=request.POST,
                                            prefix='per_loc', many_related_manager=person.cofkpersonlocationmap_set,
                                            data_fn=_prepare_per_loc_data,
                                            extra=0, )

    def _render_full_form():
        return render(request, 'person/full_form.html', {
            'person_form': person_form,
            'new_loc_form': new_loc_form,
            'loc_formset': loc_formset,
        })

    if request.POST:
        form_formsets = [person_form, new_loc_form, loc_formset]
        if view_utils.any_invalid(form_formsets):
            return _render_full_form()

        # save new person_location_map
        if target_id := new_loc_form.cleaned_data.get('target_id'):
            ps_loc: CofkPersonLocationMap = new_loc_form.instance
            ps_loc.location = CofkUnionLocation.objects.get(location_id=target_id)
            if not ps_loc.location:
                # KTODO can we put it to validate function?
                log.warning(f"location_id not found -- {target_id} ")
                return _render_full_form()

            ps_loc.person = person_form.instance
            ps_loc.relationship_type = 'was_in_location'
            ps_loc.update_current_user_timestamp(request.user.username)
            ps_loc.save()

        # update loc_formset
        loc_target_changed_fields = {'to_date', 'from_date', 'is_delete'}
        _loc_forms = (f for f in loc_formset if not loc_target_changed_fields.isdisjoint(f.changed_data))
        for f in _loc_forms:
            if f.cleaned_data['is_delete']:
                CofkPersonLocationMap.objects.filter(pk=f.cleaned_data['recref_id']).delete()
            else:
                ps_loc = CofkPersonLocationMap.objects.get(pk=f.cleaned_data['recref_id'])
                ps_loc.to_date = f.cleaned_data['to_date']
                ps_loc.from_date = f.cleaned_data['from_date']
                ps_loc.update_current_user_timestamp(request.user.username)
                print(f.cleaned_data)
                ps_loc.save()

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
