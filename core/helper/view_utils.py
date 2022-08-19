from typing import Iterable, Tuple, List, Type
from urllib.parse import urlencode

from django import template
from django.template.loader import render_to_string
from django.views.generic import ListView

from core.forms import build_search_components
from core.helper.renderer import CompactItemRenderer

register = template.Library()


class CompactSearchResultsRenderer:
    template_name = 'core/component/search_compact_layout.html'

    def __init__(self, records):
        self.records = records

    @property
    def compact_item_renderer_factory(self) -> Type[CompactItemRenderer]:
        raise NotImplementedError('type of CompactItemRenderer have not provided ')

    def render(self):
        context = {
            'search_results': map(self.compact_item_renderer_factory, self.records)
        }
        return render_to_string(self.template_name, context)


class BasicSearchView(ListView):
    """
    Helper for you to build common style of search page for emlo editor
    """
    template_name = 'core/basic_search_page.html'
    context_object_name = 'records'

    @property
    def query_fieldset_list(self) -> Iterable:
        """
        return iterable form that can render search fieldset for searching
        """
        raise NotImplementedError()

    @property
    def title(self) -> str:
        raise NotImplementedError()

    @property
    def sort_by_choices(self) -> List[Tuple[str, str]]:
        """
        return list of tuple for "django field value" and "Label"
        Example :
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
            ('-location_name', 'Location Name desc',),
            ('location_name', 'Location Name asc',),
        ]

        """
        raise NotImplementedError()

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        raise NotImplementedError('missing compact_search_results_renderer_factory')

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_sort_by(self):
        return self.request_data.get('sort_by', self.sort_by_choices[0][0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_components_factory = build_search_components(self.sort_by_choices)

        default_search_components_dict = {
            'num_record': str(self.paginate_by),
            'sort_by': self.get_sort_by(),
        }

        context.update({'query_fieldset_list': self.query_fieldset_list,
                        'search_components': search_components_factory(default_search_components_dict |
                                                                       self.request_data.dict()),
                        'total_record': self.get_queryset().count(),
                        'title': self.title or '',
                        'results_renderer': self.compact_search_results_renderer_factory(
                            context[self.context_object_name]).render,
                        })
        return context

    def get(self, request, *args, **kwargs):
        if num_record := request.GET.get('num_record'):
            self.paginate_by = num_record

        return super().get(request, *args, **kwargs)


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        return '?{}'.format(urlencode(safe_args))
    return ''
