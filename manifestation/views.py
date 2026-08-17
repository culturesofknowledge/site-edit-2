from typing import Iterable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Lookup
from core import constant

from core.helper import renderer_serv, view_serv, query_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView
from manifestation import manif_serv
from manifestation.forms import ManifSearchFieldset
from manifestation.models import CofkUnionManifestation


class ManifSearchView(PermissionRequiredMixin, LoginRequiredMixin, DefaultSearchView):
    permission_required = constant.PM_CHANGE_WORK
    raise_exception = True

    @property
    def entity(self) -> str:
        return 'manifestation,manifestations'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('change_timestamp', 'Change Timestamp',),
            ('work__iwork_id', 'Work ID',),
            ('manifestation_type', 'Document type',),
            ('id_number_or_shelfmark', 'ID number or shelfmark',),
        ]

    @property
    def search_field_fn_maps(self) -> dict[str, Lookup]:
        return query_serv.create_from_to_datetime('change_timestamp_from',
                                                  'change_timestamp_to',
                                                  'change_timestamp')

    @property
    def search_field_combines(self) -> dict[str: list[str]]:
        return {
            'work_id': ['work__iwork_id'],
        }

    @property
    def return_quick_init_vname(self) -> str:
        return 'manif:return_quick_init'

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionManifestation.objects.none()

        return self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

    def get_queryset_by_request_data(self, request_data, sort_by=None) -> Iterable:
        queries = query_serv.create_queries_by_field_fn_maps(request_data, self.search_field_fn_maps)

        queries.extend(
            query_serv.create_queries_by_lookup_field(request_data, self.search_fields, self.search_field_combines)
        )

        # Handle document type dropdown (exact match, no lookup field)
        manif_type = request_data.get('manifestation_type')
        if manif_type:
            queries.append(Q(manifestation_type=manif_type))

        queryset = query_serv.update_queryset(
            CofkUnionManifestation.objects.all(), CofkUnionManifestation,
            queries=queries, sort_by=sort_by
        ).distinct()
        queryset = queryset.select_related('work')
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer('manif/search_table_layout.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        return [ManifSearchFieldset(self.request_data.dict())]


@login_required
def return_quick_init(request, pk):
    manif = CofkUnionManifestation.objects.select_related('work').get(pk=pk)
    return view_serv.render_return_quick_init(
        request, 'Manifestation',
        manif_serv.get_rich_display_name(manif),
        manif_serv.get_recref_target_id(manif),
    )
