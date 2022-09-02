import logging
from typing import List, Tuple, Callable, Iterable

from django.shortcuts import render, redirect
from django.views import View

from core.helper import renderer_utils
from core.helper.view_utils import DefaultSearchView
from person.forms import PersonForm
from person.models import CofkUnionPerson

log = logging.getLogger(__name__)


def init_form(request):
    person_form = PersonForm(request.POST or None)
    # KTODO implement POST
    if request.method == 'POST':
        if person_form.is_valid():
            if person_form.has_changed():
                log.info(f'person have been saved')
                person_form.instance.update_current_user_timestamp(request.user.username)
                # person_form.instance: CofkUnionPerson
                # KTODO how to define person_id
                # person_form.instance.iperson_id = model_utils.next_seq_safe(
                #     models.SEQ_NAME_COFKUNIONPERSION__IPERSON_ID)
                new_person = person_form.save()
                # return redirect('person:full_form', new_person.iperson_id)
                return redirect('person:search')  # TOBEREMOVE debugging only
            else:
                log.debug('form have no change, skip record save')
            return redirect('person:search')

    return render(request, 'person/init_form.html', {'person_form': person_form, })


def full_form(request, iperson_id):
    # KTODO
    return render(request, 'person/init_form.html', {'person_form': person_form, })


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
