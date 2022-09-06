import logging
from typing import List, Tuple, Callable, Iterable

from django.forms import BaseForm
from django.shortcuts import render, redirect
from django.views import View

from core.helper import renderer_utils, view_utils
from core.helper.view_utils import DefaultSearchView, CommonInitFormViewTemplate
from person.forms import PersonForm
from person.models import CofkUnionPerson

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


def full_form(request, iperson_id):
    person_form = PersonForm(request.POST or None)
    return render(request, 'person/full_form.html', {'person_form': person_form, })


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
