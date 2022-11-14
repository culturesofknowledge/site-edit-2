from typing import Callable, Iterable, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.db.models.lookups import LessThanOrEqual, GreaterThanOrEqual, Exact

from core.helper import renderer_utils, query_utils, view_utils
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_utils import BasicSearchView, DefaultSearchView
from manifestation import manif_utils
from manifestation.models import CofkUnionManifestation
from person.forms import GeneralSearchFieldset
from person.models import CofkUnionPerson


# Create your views here.

class ManifSearchView(LoginRequiredMixin, DefaultSearchView):
    # KTODO

    @property
    def title(self) -> str:
        return 'manifestation'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    # @property
    # def merge_page_vname(self) -> str:
    #     return 'manif:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'manif:return_quick_init'

    def get_queryset(self):
        # KTODO
        queryset = CofkUnionManifestation.objects.all()
        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('manif/search_table_layout.html')

    # @property
    # def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
    #     return renderer_utils.create_compact_renderer(item_template_name='person/compact_item.html')

    # @property
    # def query_fieldset_list(self) -> Iterable:
    #     default_values = {
    #         'foaf_name_lookup': 'starts_with',
    #     }
    #     request_data = default_values | self.request_data.dict()
    #
    #     return [GeneralSearchFieldset(request_data)]
    # @property
    # def download_csv_handler(self) -> DownloadCsvHandler:
    #     return PersonDownloadCsvHandler()


@login_required
def return_quick_init(request, pk):
    manif = CofkUnionManifestation.objects.get(pk=pk)
    return view_utils.render_return_quick_init(
        request, 'Manifestation',
        manif_utils.get_recref_display_name(manif),
        manif_utils.get_recref_target_id(manif),
    )
