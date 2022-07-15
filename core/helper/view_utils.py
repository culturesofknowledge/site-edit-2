from typing import Callable, Iterable
from urllib.parse import urlencode

from django import template
from django.template.loader import render_to_string
from django.views.generic import ListView

from core.forms import SearchComponents

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

    def get_records(self):
        return map(self.record_renderer, self.get_queryset().iterator())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        new_records = map(self.record_renderer, context[self.context_object_name])
        context.update({'query_fieldset_list': self.query_fieldset_list,
                        'search_components': SearchComponents(),
                        self.context_object_name: new_records,
                        'total_record': self.get_queryset().count(),  # KTODO test with some condition
                        'title': self.title or '',
                        })
        return context


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        return '?{}'.format(urlencode(safe_args))
    return ''
