from typing import Callable, Iterable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from core.helper import renderer_utils, view_utils
from core.helper.view_utils import DefaultSearchView
from manifestation import manif_utils
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
        if not self.request_data:
            return CofkUnionManifestation.objects.none()
        return CofkUnionManifestation.objects.all().order_by(*self.get_sort_by())

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('manif/search_table_layout.html')


@login_required
def return_quick_init(request, pk):
    manif = CofkUnionManifestation.objects.get(pk=pk)
    return view_utils.render_return_quick_init(
        request, 'Manifestation',
        manif_utils.get_recref_display_name(manif),
        manif_utils.get_recref_target_id(manif),
    )
