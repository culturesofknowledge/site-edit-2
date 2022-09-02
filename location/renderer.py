from typing import Type

from core.helper import renderer_utils
from core.helper.renderer_utils import CompactSearchResultsRenderer, SearchRecordRenderer


class LocationCompactSearchResultsRenderer(CompactSearchResultsRenderer):
    class _LocSRR(SearchRecordRenderer):

        @property
        def template_name(self):
            return 'location/compact_item.html'

    @property
    def record_renderer_factory(self) -> Type[SearchRecordRenderer]:
        return self._LocSRR


location_table_search_result_renderer = renderer_utils.create_table_search_results_renderer(
    'location/search_table_layout.html'
)
