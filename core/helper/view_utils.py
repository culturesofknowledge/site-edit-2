from typing import Callable, Iterable, Tuple, List
from urllib.parse import urlencode

from django import template
from django.template.loader import render_to_string
from django.views.generic import ListView

from core.forms import build_search_components

register = template.Library()


class SearchResultRenderer:
    def __init__(self, record):
        self.record = record

    def __call__(self, *args, **kwargs):
        return render_to_string(self.template_name,
                                context={'record': self.record})

    @property
    def template_name(self):
        raise NotImplementedError('please define search result template')


class BasicSearchView(ListView):
    """
    Helper for you to build common style of search page for emlo editor
    """
    template_name = 'core/basic_search_page.html'
    context_object_name = 'records'

    @property
    def record_renderer(self) -> Callable:
        """
        return renderer factory function
        that created function can convert search result record to html
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_records(self):
        return map(self.record_renderer, self.get_queryset().iterator())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_components_factory = build_search_components(self.sort_by_choices)
        new_records = map(self.record_renderer, context[self.context_object_name])
        context.update({'query_fieldset_list': self.query_fieldset_list,
                        'search_components': search_components_factory(self.request_data),
                        self.context_object_name: new_records,
                        'total_record': self.get_queryset().count(),  # KTODO test with some condition
                        'title': self.title or '',
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
