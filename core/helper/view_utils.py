import dataclasses
import logging
import os
from collections import defaultdict
from multiprocessing import Process
from typing import Iterable, Type, Callable, Any
from typing import NoReturn
from urllib.parse import urlencode

from django import template
from django.db import models
from django.db.models import Q
from django.forms import ModelForm
from django.forms import formset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

import core.constant as core_constant
from core.forms import build_search_components
from core.helper import file_utils, email_utils, query_utils, general_model_utils, recref_utils
from core.helper.model_utils import ModelLike, RecordTracker
from core.helper.renderer_utils import CompactSearchResultsRenderer, DemoCompactSearchResultsRenderer, \
    demo_table_search_results_renderer
from core.helper.view_components import DownloadCsvHandler

register = template.Library()
log = logging.getLogger(__name__)


class BasicSearchView(ListView):
    """
    Helper for you to build common style of search page for emlo editor
    """
    paginate_by = 100
    template_name = 'core/basic_search_page.html'
    context_object_name = 'records'

    @property
    def query_fieldset_list(self) -> Iterable:
        """
        return iterable form that can render search fieldset for searching
        """
        raise NotImplementedError()

    @property
    def entity(self) -> str:
        """
        return str containing singular and plural for entity separated by a comma
        """
        raise NotImplementedError()

    def expanded_query_fieldset_list(self) -> Iterable:
        """
        return iterable form for expanded view that can render search fieldset for searching
        """
        return self.query_fieldset_list

    @property
    def title(self) -> str:
        raise NotImplementedError()

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
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
    def default_sort_by_choice(self) -> int:
        return 0

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
    def merge_page_vname(self) -> str:
        # KTODO merge feature can be disable
        raise NotImplementedError('missing merge_page_vname')

    @property
    def return_quick_init_vname(self) -> str | None:
        """
        view name for "return quick init" j(select for recref)
        return None if this entity (e.g. audit) not support "return quick init"
        """
        return None

    def get_queryset(self):
        raise NotImplementedError('missing get_queryset')

    def create_queryset_by_queries(self, model_class: Type[models.Model], queries: Iterable[Q]):
        queryset = model_class.objects.all()

        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)

        return queryset

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_sort_by(self):
        if self.request_data.get('order') == 'desc':
            return '-' + self.request_data.get('sort_by', self.sort_by_choices[self.default_sort_by_choice][0])

        return self.request_data.get('sort_by', self.sort_by_choices[self.default_sort_by_choice][0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recref_mode'] = self.request_data.get('recref_mode', '0')

        search_components_factory = build_search_components(self.sort_by_choices, self.entity.split(',')[1].title())

        default_search_components_dict = {
            'num_record': str(self.paginate_by),
            'sort_by': self.get_sort_by(),
            'order': self.request_data.get('order') or 'asc'
        }
        is_compact_layout = (self.request_data.get('display-style', core_constant.SEARCH_LAYOUT_TABLE)
                             == core_constant.SEARCH_LAYOUT_GRID)
        results_renderer = (self.compact_search_results_renderer_factory
                            if is_compact_layout
                            else self.table_search_results_renderer_factory)

        query_fieldset_list = self.query_fieldset_list if is_compact_layout else self.expanded_query_fieldset_list

        context.update({'query_fieldset_list': query_fieldset_list,
                        'search_components': search_components_factory(default_search_components_dict |
                                                                       self.request_data.dict()),
                        'entity': self.entity or '',
                        'title': self.entity.split(',')[1].title() if self.entity else 'Title',
                        'results_renderer': results_renderer(self.get_search_results_context(context)),
                        'is_compact_layout': is_compact_layout,
                        'to_user_messages': getattr(self, 'to_user_messages', []),
                        'merge_page_url': reverse(self.merge_page_vname),
                        })

        if self.return_quick_init_vname:
            context['return_quick_init_vname'] = self.return_quick_init_vname

        return context

    def get_search_results_context(self, context):
        return context[self.context_object_name]

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
        log.info(f'csv file email have be send to [{to_email}]')
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
        Process(target=_fn).start()

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
    def title(self) -> str:
        return '__title__'

    @property
    def query_fieldset_list(self) -> Iterable:
        return []

    @property
    def entity(self) -> str:
        return '__ENTITIES__,__ENTITY__'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
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
    def merge_page_vname(self) -> str:
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
        _new_instance = form.save()
        log.info(f'records saved [{_new_instance}]')
        return _new_instance

    def post(self, request, *args, **kwargs):
        form = self.form_factory(request.POST or None)
        if form.is_valid() and form.has_changed():
            log.info(f'form have been changed')
            new_instance = self.on_form_changed(request, form)
            return self.resp_after_saved(request, form, new_instance)
        else:
            log.warning(f'ignore save init form -- valid[{form.is_valid()}] has_changed[{form.has_changed()}]')

        return self.resp_form_page(request, form)

    def get(self, request, *args, **kwargs):
        form = self.form_factory()
        return self.resp_form_page(request, form)


def render_return_quick_init(request, name, item_name, item_id):
    return render(request, 'core/return_quick_init.html', {
        'name': name,
        'item_name': item_name,
        'item_id': item_id,
    })


def any_invalid_with_log(form_formsets: Iterable):
    for f in form_formsets:
        if not f.is_valid():
            log.debug(f'form is invalid [{type(f)}] '
                      f'-- [{getattr(f, "error_messages", None)}] '
                      f'-- [{repr(getattr(f, "errors", None))}]')
            return True

    return False


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


class FormDescriptor:

    def __init__(self, obj: ModelLike):
        self.obj = obj

    @property
    def name(self):
        """ name of the records """
        return '__unknown_name__'

    @property
    def model_name(self):
        """ mode name of records e.g. (Work, Person, Location) """
        return '__unknown_title__'

    @property
    def id(self):
        """ id of record"""
        return self.obj and self.obj.pk

    @property
    def change_timestamp(self):
        if isinstance(self.obj, RecordTracker):
            return self.obj.change_timestamp
        return None

    @property
    def change_user(self):
        if isinstance(self.obj, RecordTracker):
            return self.obj.change_user
        return None

    def create_context(self):
        return {'form_descriptor': self}


@dataclasses.dataclass
class MergeChoiceContext:
    model_pk: Any
    name: str
    related_records: list[tuple[str, list[str]]]


def get_parent_related_field(bounded_data, parent_model):
    return recref_utils.get_parent_related_field(*list(bounded_data.pair), parent_model)


def create_merge_choice_context(model: ModelLike) -> 'MergeChoiceContext':
    name = general_model_utils.get_display_name(model)

    bounded_data_list = recref_utils.find_bounded_data_list_by_related_model(model)
    related_records = []
    for bounded_data in bounded_data_list:
        parent_field, related_field = get_parent_related_field(bounded_data, model)
        recref_list = list(recref_utils.find_recref_list_by_bounded_data(bounded_data, model))
        if recref_list:
            related_records.append((general_model_utils.get_name_by_model_class(related_field.field.related_model),
                                    [get_recref_ref_name(related_field, r) for r in recref_list]))
    return MergeChoiceContext(model_pk=model.pk, name=name, related_records=related_records)


class MergeChoiceViews(View):

    def to_context_list(self, merge_id_list: list[str]) -> Iterable['MergeChoiceContext']:
        raise NotImplementedError()

    @property
    def action_vname(self):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        id_list = request.GET.getlist('__merge_id')
        return render(request, 'core/merge_choice.html', {
            'choice_list': self.to_context_list(id_list),
            'merge_action_url': reverse(self.action_vname),
        })


def find_all_recref_by_models(model_list, parent_model):
    for model in model_list:
        for bounded_data in recref_utils.find_bounded_data_list_by_related_model(parent_model):
            records = recref_utils.find_recref_list_by_bounded_data(bounded_data, model)
            yield from records


def get_recref_ref_name(related_field, recref) -> str:
    related_model = related_field.get_object(recref)
    return '[{}] {}'.format(
        related_model.pk,
        general_model_utils.get_display_name(related_model)
    )


class MergeActionViews(View):
    @property
    def target_model_class(self) -> Type[ModelLike]:
        raise NotImplementedError()

    @property
    def return_vname(self) -> str:
        """ vname for return button """
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        selected_pk = request.POST.get('selected_pk')
        merge_pk_list = set(request.POST.getlist('merge_pk')) - {selected_pk}
        other_models = list(self.target_model_class.objects.filter(**{'pk__in': merge_pk_list}).iterator())
        selected_model = self.target_model_class.objects.filter(**{'pk': selected_pk}).first()
        if selected_model and len(other_models) == 0:
            log.warning('input merge_pk_list empty')
            return HttpResponseNotFound()

        results = defaultdict(list)
        for recref in find_all_recref_by_models(other_models, selected_model):
            parent_field, related_field = recref_utils.get_parent_related_field_by_recref(recref, selected_model)

            # update related_field on recref r
            related_field_name = parent_field.field.name
            log.debug(f'change related record. recref[{recref.pk}] related_name[{related_field_name}] '
                      f'from[{getattr(recref, related_field_name).pk}] to[{selected_model.pk}]')
            setattr(recref, related_field_name, selected_model)
            recref.update_current_user_timestamp(request.user.username)
            recref.save()

            results[general_model_utils.get_name_by_model_class(related_field.field.related_model)].append(
                get_recref_ref_name(related_field, recref)
            )

        # KTODO update query work if needed

        return render(request, 'core/merge_report.html', {
            'summary': results.items(),
            'return_vname': self.return_vname,
            'name': general_model_utils.get_display_name(selected_model),
        })
