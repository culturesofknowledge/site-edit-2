import logging
import os
from multiprocessing import Process
from typing import Iterable, Tuple, List, Type, Callable
from typing import NoReturn
from typing import Optional
from urllib.parse import urlencode

from django import template
from django.db import models
from django.forms import ModelForm
from django.forms import formset_factory
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

import core.constant as core_constant
from core.forms import RecrefForm
from core.forms import build_search_components
from core.helper import file_utils, email_utils
from core.helper import view_utils
from core.helper.renderer_utils import CompactSearchResultsRenderer, DemoCompactSearchResultsRenderer, \
    demo_table_search_results_renderer
from core.helper.view_components import DownloadCsvHandler

register = template.Library()
log = logging.getLogger(__name__)


class BasicSearchView(ListView):
    """
    Helper for you to build common style of search page for emlo editor
    """
    paginate_by = 5
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
    def merge_page_name(self) -> str:
        raise NotImplementedError('missing merge_page_name')

    def get_queryset(self):
        raise NotImplementedError('missing get_queryset')

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_sort_by(self):
        return self.request_data.get('sort_by', self.sort_by_choices[0][0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recref_mode'] = self.request_data.get('recref_mode', '0')

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
                        'merge_page_url': reverse(self.merge_page_name),
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
        simple_form_action_map = {
            'download_csv': self.resp_download_csv,
        }

        # simple routing with __form_action
        if resp_fn := simple_form_action_map.get(self.request_data.get("__form_action")):
            return resp_fn(request, *args, **kwargs)

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


class DefaultSearchView(BasicSearchView):

    @property
    def query_fieldset_list(self) -> Iterable:
        return []

    @property
    def title(self) -> str:
        return '__TITLE__'

    @property
    def sort_by_choices(self) -> List[Tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return DemoCompactSearchResultsRenderer

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return demo_table_search_results_renderer

    @property
    def download_csv_handler(self) -> DownloadCsvHandler:
        return None

    @property
    def merge_page_name(self) -> View:
        return 'login:gate'

    def get_queryset(self):
        class _FakeQueryset(list):

            def count(self, *args, **kwargs):
                return 0

        return _FakeQueryset()


class CommonInitFormViewTemplate(View):

    def resp_form_page(self, request, form):
        raise NotImplementedError()

    def resp_after_saved(self, request, form, new_instance):
        raise NotImplementedError()

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        raise NotImplementedError()

    def on_form_changed(self, request, form) -> NoReturn:
        if hasattr(form.instance, 'update_current_user_timestamp'):
            form.instance.update_current_user_timestamp(request.user.username)
        _new_loc = form.save()
        return _new_loc

    def post(self, request, *args, **kwargs):
        form = self.form_factory(request.POST or None)
        if form.is_valid():
            log.info(f'form have been changed')
            new_instance = self.on_form_changed(request, form)
            return self.resp_after_saved(request, form, new_instance)

        return self.resp_form_page(request, form)

    def get(self, request, *args, **kwargs):
        form = self.form_factory()
        return self.resp_form_page(request, form)


def redirect_return_quick_init(request, name, item_name, item_id):
    return render(request, 'core/return_quick_init.html', {
        'name': 'Person',
        'item_name': item_name,
        'item_id': item_id,
    })


def any_invalid(form_formsets: Iterable):
    return not all(f.is_valid() for f in form_formsets)


def create_formset(form_class, post_data=None, prefix=None,
                   initial_list: Iterable[dict] = None,
                   extra=1):
    initial_list = initial_list or []
    initial_list = list(initial_list)
    return formset_factory(form_class, extra=extra)(
        post_data or None,
        prefix=prefix,
        initial=initial_list,
    )


class MultiRecrefHandler:
    """
    provide common workflow handle multi recref records
    * create, delete , update record
    * create form and formset
    """

    def __init__(self, request_data, name, initial_list=None):

        self.name = name
        self.new_form = RecrefForm(request_data or None, prefix=f'new_{name}')
        self.update_formset = view_utils.create_formset(RecrefForm, post_data=request_data,
                                                        prefix=f'recref_{name}',
                                                        initial_list=initial_list,
                                                        extra=0, )

    def create_context(self) -> dict:
        return {
            f'recref_{self.name}': {
                'new_form': self.new_form,
                'update_formset': self.update_formset,
            },
        }

    @property
    def recref_class(self) -> Type[models.Model]:
        raise NotImplementedError()

    @staticmethod
    def fill_common_recref_field(recref, cleaned_data, username):
        recref.to_date = cleaned_data.get('to_date')
        recref.from_date = cleaned_data.get('from_date')
        recref.update_current_user_timestamp(username)
        return recref

    def create_recref_by_new_form(self, target_id, new_form, parent_instance) -> Optional[models.Model]:
        raise NotImplementedError()

    def maintain_record(self, request, parent_instance):
        """
        workflow for handle:
        create, update, delete recref record by form data
        """
        # save new_form
        self.new_form.is_valid()
        if target_id := self.new_form.cleaned_data.get('target_id'):
            if recref := self.create_recref_by_new_form(target_id, self.new_form, parent_instance):
                recref = self.fill_common_recref_field(recref, self.new_form.cleaned_data, request.user.username)
                recref.save()

        # update update_formset
        target_changed_fields = {'to_date', 'from_date', 'is_delete'}
        _forms = (f for f in self.update_formset if not target_changed_fields.isdisjoint(f.changed_data))
        for f in _forms:
            f.is_valid()
            if f.cleaned_data['is_delete']:
                self.recref_class.objects.filter(pk=f.cleaned_data['recref_id']).delete()
            else:
                ps_loc = self.recref_class.objects.get(pk=f.cleaned_data['recref_id'])
                ps_loc = self.fill_common_recref_field(ps_loc, f.cleaned_data, request.user.username)
                print(f.cleaned_data)  # TOBEREMOVE
                ps_loc.save()
