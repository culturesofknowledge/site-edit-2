import logging
import os
from multiprocessing import Process
from typing import Iterable, Tuple, List, Type, Callable
from urllib.parse import urlencode

from django import template
from django.views.generic import ListView

import core.constant as core_constant
from core.forms import build_search_components
from core.helper import file_utils, email_utils
from core.helper.renderer import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler

register = template.Library()
log = logging.getLogger(__name__)


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
        """ factory of Compact layout """
        raise NotImplementedError('missing compact_search_results_renderer_factory')

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        """ factory of Table layout """
        raise NotImplementedError('missing table_search_results_renderer_factory')

    @property
    def download_csv_handler(self) -> DownloadCsvHandler:
        raise NotImplementedError('missing download_csv_handler')

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
        is_compact_layout = (self.request_data.get('display-style', core_constant.SEARCH_LAYOUT_TABLE)
                             == core_constant.SEARCH_LAYOUT_GRID)
        results_renderer = (self.compact_search_results_renderer_factory
                            if is_compact_layout
                            else self.table_search_results_renderer_factory)

        context.update({'query_fieldset_list': self.query_fieldset_list,
                        'search_components': search_components_factory(default_search_components_dict |
                                                                       self.request_data.dict()),
                        'total_record': self.get_queryset().count(),
                        'title': self.title or '',
                        'results_renderer': results_renderer(context[self.context_object_name]),
                        'is_compact_layout': is_compact_layout,
                        'to_user_messages': getattr(self, 'to_user_messages', []),
                        })

        return context

    @staticmethod
    def send_csv_email(csv_handler, queryset, to_email):
        csv_path = file_utils.create_new_tmp_file_path()
        csv_handler.create_csv_file(csv_path, queryset)

        if not to_email:
            log.error(f'unknown user email -- [{to_email}]')

        resp = email_utils.send_email(
            to_email,
            subject='Search result',
            attachments=[
                ('search_result.csv', open(csv_path, mode='rb'), 'text/csv')
            ],
        )
        os.remove(csv_path)
        log.debug('email resp', resp)

    def resp_download_csv(self, request, *args, **kwargs):

        def _fn():
            try:
                self.send_csv_email(self.download_csv_handler, self.get_queryset(), request.user.email)
            except Exception as e:
                log.error('send csv email fail....')
                log.exception(e)

        # create csv file and send email in other process
        Process(target=_fn).run()

        # stay as same page
        self.to_user_messages = ['Csv file will be send to your email later.']
        return super().get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        # response for download_csv
        if self.request_data.get("__form_action") == 'download_csv':
            return self.resp_download_csv(request, *args, **kwargs)

        if num_record := request.GET.get('num_record'):
            self.paginate_by = num_record

        # response for search query
        return super().get(request, *args, **kwargs)


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        return '?{}'.format(urlencode(safe_args))
    return ''
