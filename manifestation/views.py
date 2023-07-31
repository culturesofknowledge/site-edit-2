from typing import Callable, Iterable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from core.helper import renderer_serv, view_serv, query_serv
from core.helper.view_serv import DefaultSearchView
from manifestation import manif_serv
from manifestation.models import CofkUnionManifestation


class ManifSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def entity(self) -> str:
        return 'manifestation,manifestations'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('change_timestamp', 'Change Timestamp',),
        ]

    @property
    def return_quick_init_vname(self) -> str:
        return 'manif:return_quick_init'

    def get_queryset(self):
        queryset = CofkUnionManifestation.objects.all()
        queryset = query_serv.update_queryset(queryset, CofkUnionManifestation, sort_by=self.get_sort_by())
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_serv.create_table_search_results_renderer('manif/search_table_layout.html')


@login_required
def return_quick_init(request, pk):
    manif = CofkUnionManifestation.objects.get(pk=pk)
    return view_serv.render_return_quick_init(
        request, 'Manifestation',
        manif_serv.get_recref_display_name(manif),
        manif_serv.get_recref_target_id(manif),
    )
