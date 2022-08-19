from typing import Type

from django.template.loader import render_to_string

from core.helper.renderer import CompactSearchResultsRenderer, SearchRecordRenderer


class LocationCompactSearchResultsRenderer(CompactSearchResultsRenderer):
    class _LocSRR(SearchRecordRenderer):

        @property
        def template_name(self):
            return 'location/compact_item.html'

    @property
    def record_renderer_factory(self) -> Type[SearchRecordRenderer]:
        return self._LocSRR


class LocationTableSearchResultsRenderer:

    def __init__(self, records):
        self.records = records

    def __call__(self):
        context = {
            'search_results': self.records
        }
        return render_to_string('location/search_table_layout.html', context)
