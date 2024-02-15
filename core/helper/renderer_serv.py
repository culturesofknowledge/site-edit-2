from typing import Type, Callable, Iterable

from django.template.loader import render_to_string

Renderer = Callable[[], str]
RendererFactory = Callable[[Iterable], Renderer]

class SearchRecordRenderer:
    """ renderer for one record
    """

    def __init__(self, record, record_name='record'):
        self.record = record
        self.record_name = record_name

    def __call__(self):
        return render_to_string(self.template_name,
                                context={self.record_name: self.record})

    @property
    def template_name(self):
        raise NotImplementedError('please define search result template')


def create_search_record_renderer(selected_template_name: str) -> Type[SearchRecordRenderer]:
    class NewSearchRecordRender(SearchRecordRenderer):
        @property
        def template_name(self):
            return selected_template_name

    return NewSearchRecordRender


class CompactSearchResultsRenderer:
    """ renderer for all records as common compact layout
    """
    template_name = 'core/component/search_compact_layout.html'

    def __init__(self, records):
        self.records = records

    def __call__(self):
        context = {
            'search_results': map(self.record_renderer_factory, self.records)
        }
        return render_to_string(self.template_name, context)

    @property
    def record_renderer_factory(self) -> Type[SearchRecordRenderer]:
        raise NotImplementedError('type of SearchRecordRenderer have not provided ')


def create_compact_renderer(
        item_template_name: str = None,
        item_renderer_factory: Type[SearchRecordRenderer] = None
) -> Type[CompactSearchResultsRenderer]:
    if (item_template_name is None
            and item_renderer_factory is None):
        raise ValueError('select template_name or renderer_factory to create compact_renderer')

    if item_template_name:
        item_renderer_factory = create_search_record_renderer(item_template_name)

    class NewCompactSearchResultsRenderer(CompactSearchResultsRenderer):
        @property
        def record_renderer_factory(self) -> Type[SearchRecordRenderer]:
            return item_renderer_factory

    return NewCompactSearchResultsRenderer


def create_table_search_results_renderer(template_path, records_name='search_results', ):
    def _renderer_by_record(records):
        def _render():
            context = {
                records_name: records
            }
            return render_to_string(template_path, context)

        return _render

    return _renderer_by_record


class DemoCompactSearchResultsRenderer(CompactSearchResultsRenderer):
    class _DemoSRR(SearchRecordRenderer):

        @property
        def template_name(self):
            return 'core/demo_compact_item.html'

    @property
    def record_renderer_factory(self) -> Type[SearchRecordRenderer]:
        return self._DemoSRR


demo_table_search_results_renderer = create_table_search_results_renderer(
    'core/demo_search_table_layout.html',
)
