import dataclasses
import itertools
import logging
import urllib
from collections import defaultdict
from datetime import datetime
from threading import Thread
from typing import Iterable, Type, Callable, Any, TYPE_CHECKING, List
from typing import NoReturn
from urllib.parse import urljoin

from django import template
from django.conf import settings
from django.db import models
from django.db.models import Q, ForeignKey, QuerySet
from django.db.models.query_utils import DeferredAttribute
from django.forms import ModelForm
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

import core.constant as core_constant
from core import constant
from core.form_label_maps import field_label_map
from core.helper import query_utils, general_model_utils, recref_utils, model_utils, \
    url_utils, date_utils, perm_utils, media_service
from sharedlib import inspect_utils, str_utils
from sharedlib.djangolib import django_utils, email_utils
from core.helper.form_utils import build_search_components
from core.helper.model_utils import ModelLike, RecordTracker
from core.helper.renderer_utils import CompactSearchResultsRenderer, DemoCompactSearchResultsRenderer, \
    demo_table_search_results_renderer
from core.helper.url_utils import VNAME_FULL_FORM, VNAME_SEARCH
from core.helper.view_components import DownloadCsvHandler
from core.models import CofkUnionResource, CofkUnionComment, CofkUserSavedQuery, CofkUserSavedQuerySelection
from work.models import CofkUnionWork

if TYPE_CHECKING:
    from core.models import Recref
    from django.db.models import QuerySet

register = template.Library()
log = logging.getLogger(__name__)


def send_email_file_by_url(file_name, to_email):
    if not to_email:
        log.error(f'unknown user email -- [{to_email}]')
        return

    download_path = reverse('file-download', kwargs={'file_path': file_name})
    download_url = urljoin(settings.EXPORT_ROOT_URL, download_path)
    content = f'file can be download from this url: {download_url}'
    resp = email_utils.send_email(to_email,
                                  subject='Search result',
                                  content=content, )
    log.info(f'file email have be send to [{to_email}]')
    log.debug(f'email resp {resp}')


def create_export_file_name(name, suffix):
    return '{}_{}_{}.{}'.format(name,
                                date_utils.date_to_simple_date_str(datetime.utcnow()),
                                str_utils.create_random_str(10),
                                suffix)


class BasicSearchView(ListView):
    """
    Helper for you to build common style of search page for emlo editor
    """
    paginate_by = 100
    template_name = 'core/basic_search_page.html'
    context_object_name = 'records'

    @property
    def search_field_label_map(self) -> dict:
        """
        A dictionary mapping between the model field name and the labelling of that field.

        Only used by self.simplified_query.
        """
        if self.app_name in field_label_map:
            return field_label_map[self.app_name]

        return {}

    @property
    def search_fields(self) -> List[str]:
        """
        A list of fields searched directly on.

        'Change_timestamp' is excluded because it is a range.
        """
        exclude = ['change_timestamp_from', 'change_timestamp_to']
        return [f for f in self.search_field_label_map.keys() if f not in exclude]

    @property
    def search_field_fn_maps(self) -> dict:
        """
        A dictionary mapping between form field names where there is more than one field to search against
        simultaneously, such as with ranges.

        Used with query_utils.create_queries_by_field_fn_maps and query_utils.create_from_to_datetime for instance.
        """
        raise NotImplementedError()

    @property
    def search_field_combines(self) -> dict[str: List[str]]:
        """
        A dictionary mapping between search multiple fields under one form field.
        """
        raise NotImplementedError()

    @property
    def simplified_query(self) -> list[str]:
        """
        returns a simplified, human-readable version of the search criteria, this is inserted into the context at
        self.get_context_data
        """
        simplified_query = []

        for field_name in self.search_fields:
            field_val = self.request_data.get(field_name)

            if (field_val is not None and field_val != '') or (
                    field_name in self.request_data and f'{field_name}_lookup' in self.request_data and
                    'blank' in self.request_data.get(f'{field_name}_lookup')):
                label_name = self.search_field_label_map.get(field_name) or field_name.replace('_', ' ').capitalize()
                lookup_key = self.request_data.get(f'{field_name}_lookup').replace('_', ' ')

                if 'blank' in lookup_key:
                    simplified_query.append(f'{label_name} {lookup_key}.')
                else:
                    if lookup_key.startswith('not'):
                        lookup_key = 'does ' + lookup_key

                    simplified_query.append(f'{label_name} {lookup_key} "{field_val}".')

        if self.search_field_fn_maps:
            _from = self.request_data['change_timestamp_from'] if 'change_timestamp_from' in self.request_data else None
            _to = self.request_data['change_timestamp_to'] if 'change_timestamp_to' in self.request_data else None

            if _to and _from:
                simplified_query.append(f'Last edited between {_from} and {_to}.')
            elif _to:
                simplified_query.append(f'Last edited before {_to}.')
            elif _from:
                simplified_query.append(f'Last edited after {_from}.')

        return simplified_query

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

    @property
    def app_name(self) -> str:
        return self.request.resolver_match.app_name

    def expanded_query_fieldset_list(self) -> Iterable:
        """
        return iterable form for expanded view that can render search fieldset for searching
        """
        return self.query_fieldset_list

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        """
        return list of tuple for "django field value" and "Label"
        Example :
        return [
            ('change_timestamp', 'Change timestamp',),
            ('location_name', 'Location name',),
        ]

        """
        raise NotImplementedError()

    @property
    def default_sort_by_choice(self) -> int:
        return 0

    @property
    def default_order(self) -> str:
        """
        Ascending or descending ('asc' or 'desc')
        """
        return 'asc'

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        """ factory of Compact layout """
        raise NotImplementedError('missing compact_search_results_renderer_factory')

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        """ factory of Table layout """
        raise NotImplementedError('missing table_search_results_renderer_factory')

    @property
    def csv_export_setting(self) -> tuple[Callable[[], str], Callable[[], DownloadCsvHandler]] | None:
        """
        overrider this to enable download csv
        :return:
        - fn of csv file name
        - fn of DownloadCsvHandler
        - permission list
        or
        - None if this entity (e.g. audit) not support csv export
        """
        return None

    @property
    def excel_export_setting(self) -> tuple[Callable[[], str], Callable[[Iterable, str], Any]] | None:
        """ overrider this to enable download csv """
        return None

    @property
    def merge_page_vname(self) -> str | None:
        return None

    @property
    def return_quick_init_vname(self) -> str | None:
        """
        view name for "return quick init" j(select for recref)
        return None if this entity (e.g. audit) not support "return quick init"
        """
        return None

    def get_queryset(self):
        raise NotImplementedError('missing get_queryset')

    def create_queryset_by_queries(self, model_class: Type[models.Model],
                                   queries: Iterable[Q],
                                   sort_by: str | None = None) -> 'QuerySet':
        queryset = model_class.objects.all()

        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by is None:
            sort_by = self.get_sort_by()

        if sort_by:
            queryset = queryset.order_by(*sort_by)

        log.debug(f'search sql\n: {str(queryset.query)}')
        return queryset

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_sort_by(self, field_name=False) -> List[str]:
        sort_by = self.request_data.get('sort_by')

        # Sort not present or invalid
        if sort_by is None or sort_by not in [s[0] for s in self.sort_by_choices]:
            sort_by = self.sort_by_choices[self.default_sort_by_choice][0]

        # If caller only needs the field name
        if field_name:
            return sort_by

        # Check if it's a combined field
        if sort_by in self.search_field_combines:
            sort_by = self.search_field_combines[sort_by]
        else:
            sort_by = [sort_by]

        # Assign correct order
        if self.request_data.get('order', self.default_order) == 'desc':
            return [f'-{s}' for s in sort_by]

        return sort_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recref_mode'] = self.request_data.get('recref_mode', '0')

        search_components_factory = build_search_components(self.sort_by_choices, self.entity.split(',')[1].title())

        default_search_components_dict = {
            'num_record': str(self.paginate_by),
            'sort_by': self.get_sort_by(field_name=True),
            'order': self.request_data.get('order') or self.default_order
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
                        'simplified_query': self.simplified_query,
                        'paginate_by': self.paginate_by,
                        'can_export_csv': self.csv_export_setting is not None,
                        'can_export_excel': self.excel_export_setting is not None,
                        })

        if self.merge_page_vname:
            context['merge_page_url'] = reverse(self.merge_page_vname)

        if self.return_quick_init_vname:
            context['return_quick_init_vname'] = self.return_quick_init_vname

        return context

    def get_search_results_context(self, context):
        return context[self.context_object_name]

    def resp_file_download(self, request,
                           file_fn: Callable[[], str],
                           *args, **kwargs):

        def _fn():
            try:
                log.debug(f'start send email[{request.user}]....')
                file_name = file_fn()
                send_email_file_by_url(file_name, request.user.email)
            except Exception as e:
                log.error('send email fail....')
                log.exception(e)

        if not request.user or not request.user.email:
            msg = f'Your account[{request.user}] have no email, please contact admin.'
        else:
            # create file and send email in other thread
            Thread(target=_fn).start()
            msg = 'The selected data is being processed and will be sent to your email soon.'
        self.add_to_user_messages(msg)

        # stay as same page
        return super().get(request, *args, **kwargs)

    def save_query(self, request, *args, **kwargs):
        sort_descending = 1 if request.GET.get('order', self.default_order) == 'desc' else 0

        saved_query = CofkUserSavedQuery(username=self.request.user,
                                         query_class=self.app_name,
                                         query_order_by=request.GET.get('sort_by', self.get_sort_by(True)),
                                         query_sort_descending=sort_descending,
                                         query_entries_per_page=request.GET.get('num_record', str(self.paginate_by)),
                                         )

        selections = []
        all_search_fields = self.search_fields + list(self.search_field_fn_maps.keys()) \
                            + list(self.search_field_combines.keys())

        for key in (key for key, value in request.GET.items() if key in all_search_fields and value != ''):
            selections.append(CofkUserSavedQuerySelection(query=saved_query,
                                                          column_name=key,
                                                          op_value=request.GET[key + '_lookup'],
                                                          column_value=request.GET[key]))

        saved_query.save()
        CofkUserSavedQuerySelection.objects.bulk_create(selections)

        # stay as same page
        self.to_user_messages = ['The current search results have been saved.']
        return super().get(request, *args, **kwargs)

    def resp_download_by_export_setting(self, request, export_setting, *args, **kwargs):
        file_name_factory, file_factory, perms = export_setting
        if perms and (user := request.user):
            perm_utils.validate_permission_denied(user, perms)

        def file_fn():
            file_name = file_name_factory()
            tmp_path = media_service.FILE_DOWNLOAD_PATH.joinpath(file_name)
            file_factory()(self.get_queryset().iterator(), tmp_path)
            return file_name

        return self.resp_file_download(request, file_fn, *args, **kwargs)

    def resp_download_csv(self, request, *args, **kwargs):
        return self.resp_download_by_export_setting(request, self.csv_export_setting, *args, **kwargs)

    def resp_download_excel(self, request, *args, **kwargs):
        return self.resp_download_by_export_setting(request, self.excel_export_setting, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if to_user_messages := request.GET.get('to_user_messages'):
            self.add_to_user_messages(to_user_messages)

        simple_form_action_map = {
            'download_csv': self.resp_download_csv,
            'download_excel': self.resp_download_excel,
            'save_query': self.save_query
        }

        # simple routing with __form_action
        if resp_fn := simple_form_action_map.get(self.request_data.get("__form_action")):
            return resp_fn(request, *args, **kwargs)

        if num_record := request.GET.get('num_record'):
            self.paginate_by = num_record

        # response for search query
        return super().get(request, *args, **kwargs)

    def add_to_user_messages(self, message):
        if not hasattr(self, 'to_user_messages'):
            self.to_user_messages = []
        self.to_user_messages.append(message)

    def has_perms(self, perms: list[str]):
        return hasattr(self.request, 'user') and self.request.user.has_perms(perms)


class DefaultSearchView(BasicSearchView):

    @property
    def search_field_fn_maps(self) -> dict:
        """
        return
        """
        return {}

    @property
    def search_field_combines(self) -> dict[str: List[str]]:
        return {}

    @property
    def query_fieldset_list(self) -> Iterable:
        return []

    @property
    def entity(self) -> str:
        return '__ENTITIES__,__ENTITY__'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('change_timestamp', 'Change timestamp',),
        ]

    @property
    def default_order(self) -> str:
        return 'desc'

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return DemoCompactSearchResultsRenderer

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return demo_table_search_results_renderer

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


class MergeChoiceViews(View):

    def to_context_list(self, merge_id_list: list[str]) -> Iterable['MergeChoiceContext']:
        raise NotImplementedError()

    @staticmethod
    def get_id_field():
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        id_list = request.GET.getlist('__merge_id')
        return render(request, 'core/merge_choice.html', {
            'choice_list': self.to_context_list(id_list),
            'merge_action_url': url_utils.reverse_url_by_request(url_utils.VNAME_MERGE_CONFIRM, request),
            'return_url': url_utils.reverse_url_by_request(url_utils.VNAME_SEARCH, request),
        })

    @staticmethod
    def create_work_recref_map(recref_list: list['Recref']):

        def _name_key(rel_type: str):
            if rel_type in [constant.REL_TYPE_CREATED,
                            constant.REL_TYPE_SENT,
                            constant.REL_TYPE_SIGNED,
                            ]:
                return "Work [Author/sender of]"
            elif rel_type in [constant.REL_TYPE_WAS_ADDRESSED_TO,
                              constant.REL_TYPE_INTENDED_FOR, ]:
                return 'Work [Addressee of]'
            elif rel_type == constant.REL_TYPE_WAS_SENT_FROM:
                return 'Work [Origin]'
            elif rel_type == constant.REL_TYPE_WAS_SENT_TO:
                return 'Work [Destination]'
            else:
                return 'Work'

        recref_dict = defaultdict(list)
        for r in recref_list:
            recref_dict[_name_key(r.relationship_type)].append(r)
        return recref_dict

    @staticmethod
    def create_merge_choice_context(model: ModelLike) -> 'MergeChoiceContext':
        name = general_model_utils.get_display_name(model)

        bounded_data_list = recref_utils.find_bounded_data_list_by_related_model(model)
        related_records = []
        for bounded_data in bounded_data_list:
            _, related_field = recref_utils.get_parent_related_field_by_bounded_data(bounded_data, model)
            recref_list = list(recref_utils.find_recref_list_by_bounded_data(bounded_data, model))
            if not recref_list:
                continue

            related_model = related_field.field.related_model
            if inspect_utils.issubclass_safe(related_model, CofkUnionWork):
                for _name, _recref_list in MergeChoiceViews.create_work_recref_map(recref_list).items():
                    related_records.append((_name,
                                            [get_recref_ref_name(related_field, r) for r in _recref_list]))
            else:
                related_records.append((general_model_utils.get_name_by_model_class(related_model),
                                        [get_recref_ref_name(related_field, r) for r in recref_list]))

        return MergeChoiceContext(model_pk=model.pk, name=name, related_records=related_records)

    @staticmethod
    def create_merge_choice_context_by_id_field(field: DeferredAttribute, merge_id_list: list):
        records = field.field.model.objects.filter(
            **{
                f'{field.field.name}__in': merge_id_list
            }
        ).iterator()
        return (MergeChoiceViews.create_merge_choice_context(m) for m in records)


def find_all_recref_by_models(model_list):
    for model in model_list:
        for bounded_data in recref_utils.find_bounded_data_list_by_related_model(model):
            records = recref_utils.find_recref_list_by_bounded_data(bounded_data, model)
            yield from records


def get_recref_ref_name(related_field, recref) -> str:
    related_model = related_field.get_object(recref)
    if isinstance(related_model, CofkUnionComment):
        return '[{}] {}'.format(
            related_model.pk,
            general_model_utils.get_display_name(related_model)
        )
    elif isinstance(related_model, CofkUnionResource):
        return '{} ({}) '.format(
            general_model_utils.get_display_name(related_model),
            related_model.resource_url,
        )
    else:
        return general_model_utils.get_display_name(related_model)


def find_work_by_recref_list(recref_list: Iterable['Recref']):
    pk_set = set()
    for recref in recref_list:
        field = model_utils.get_related_field(recref.__class__, CofkUnionWork)
        if field is None:
            continue

        work = getattr(recref, field.name)
        if work.pk not in pk_set:
            pk_set.add(work.pk)
            yield work


def find_related_collect_field(target_model_class: Type[ModelLike]) -> Iterable[tuple[Type[ModelLike], ForeignKey]]:
    def _is_target_field(f):
        return isinstance(f, ForeignKey) and inspect_utils.issubclass_safe(f.related_model, target_model_class)

    _models = django_utils.all_model_classes()
    _models = (m for m in _models if m.__name__.startswith('CofkCollect'))
    _models = itertools.chain.from_iterable(
        ((m, f) for f in m._meta.fields if _is_target_field(f))
        for m in _models)
    return _models


class MergeConfirmViews(View):

    @property
    def target_model_class(self) -> Type[ModelLike]:
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        selected_model, other_models = load_merge_parameter(request.POST, self.target_model_class)
        return render(request, 'core/merge_confirm.html', {
            'selected': MergeChoiceViews.create_merge_choice_context(selected_model),
            'others': (MergeChoiceViews.create_merge_choice_context(m) for m in other_models),
            'merge_action_url': url_utils.reverse_url_by_request(url_utils.VNAME_MERGE_ACTION, request),
        })


class MergeActionViews(View):
    @property
    def target_model_class(self) -> Type[ModelLike]:
        raise NotImplementedError()

    @staticmethod
    def merge(selected_model: ModelLike, other_models: list[ModelLike], username=None):
        if selected_model and len(other_models) == 0:
            msg = f'invalid selected_model[{selected_model}], empty other_models[{len(other_models)}] '
            log.warning(msg)
            return ValueError(msg)

        log.info('merge type[{}] selected[{}] other[{}]'.format(
            selected_model.__class__.__name__,
            selected_model.pk,
            [m.pk for m in other_models]
        ))

        recref_list: Iterable[Recref] = find_all_recref_by_models(other_models)
        recref_list = list(recref_list)
        for recref in recref_list:
            parent_field, related_field = recref_utils.get_parent_related_field_by_recref(recref, selected_model)

            # update related_field on recref
            related_field_name = parent_field.field.name
            log.debug(f'change related record. recref[{recref.pk}] related_name[{related_field_name}] '
                      f'from[{getattr(recref, related_field_name).pk}] to[{selected_model.pk}]')
            setattr(recref, related_field_name, selected_model)
            if username:
                recref.update_current_user_timestamp(username)
            recref.save()

        # change ForeignKey value to master's id in cofk_collect
        for model_class, foreign_field in find_related_collect_field(selected_model.__class__):
            new_id = foreign_field.target_field.value_from_object(selected_model)
            old_ids = [foreign_field.target_field.value_from_object(o) for o in other_models]
            outdated_records = model_class.objects.filter(**{
                f'{foreign_field.attname}__in': old_ids
            })
            log.info('update [{}.{}] with old_ids[{}] to new_id[{}], total[{}]'.format(
                model_class.__name__, foreign_field.attname,
                old_ids, new_id, outdated_records.count()
            ))
            outdated_records.update(**{foreign_field.attname: new_id})

        # remove other_models
        for m in other_models:
            log.info(f'remove [{m.__class__.__name__}] pk[{m.pk}]')
            m.delete()

        return recref_list

    @staticmethod
    def get_id_field():
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        selected_model, other_models = load_merge_parameter(request.POST, self.target_model_class)

        if request.POST.get('action_type') != 'confirm':
            query = [
                ('__merge_id', self.get_id_field().field.value_from_object(m))
                for m in [selected_model] + list(other_models)
            ]
            url = url_utils.build_url_query(
                url_utils.reverse_url_by_request(url_utils.VNAME_MERGE_CHOICE, request),
                query)
            return redirect(url)

        try:
            recref_list = self.merge(selected_model, other_models, username=request.user.username)
        except ValueError:
            return HttpResponseNotFound()

        # prepare results context
        results = defaultdict(list)
        for recref in recref_list:
            _, related_field = recref_utils.get_parent_related_field_by_recref(recref, selected_model)
            results[general_model_utils.get_name_by_model_class(related_field.field.related_model)].append(
                get_recref_ref_name(related_field, recref)
            )

        return render(request, 'core/merge_report.html', {
            'summary': results.items(),
            'return_url': url_utils.reverse_url_by_request(url_utils.VNAME_SEARCH, request),
            'name': general_model_utils.get_display_name(selected_model),
        })


def log_value_error(msg):
    log.debug(msg)
    return ValueError(msg)


def get_merge_parameter(request_data):
    selected_pk = request_data.get('selected_pk')
    merge_pk_list = set(request_data.getlist('merge_pk')) - {selected_pk}
    if not merge_pk_list:
        raise log_value_error(f'input parameter {merge_pk_list=} should not empty')
    return selected_pk, merge_pk_list


def load_merge_parameter(request_data, target_model_class):
    selected_pk, merge_pk_list = get_merge_parameter(request_data)
    other_models = list(target_model_class.objects.filter(**{'pk__in': merge_pk_list}).iterator())
    selected_model = target_model_class.objects.filter(**{'pk': selected_pk}).first()
    if not selected_model:
        raise log_value_error(f'selected_model not found [{selected_pk=}]')

    if not other_models or len(other_models) != len(merge_pk_list):
        raise log_value_error(f'some other_models not found, [{other_models=}] [{merge_pk_list=}]')

    return selected_model, other_models


def create_is_save_success_context(is_save_success) -> dict:
    context = {}
    if is_save_success:
        context = {'is_save_success': True}
    return context


def mark_callback_save_success(request) -> bool:
    callback_name = 'callback_if_save_success'
    return request.POST.get(callback_name) == '1' or request.GET.get(callback_name) == '1'


def append_callback_save_success_parameter(request, url):
    if mark_callback_save_success(request):
        url += '?callback_if_save_success=1'
    return url


class DeleteConfirmView(View):
    """
    sample delete confirm view
    for user to delete one records (Person, Location, Inst, etc)

    some title, contain can be override by subclass
    """

    def get_model_class(self) -> Type[ModelLike]:
        raise NotImplementedError()

    def get_name(self):
        """ name for display in label or title """
        return general_model_utils.get_name_by_model_class(self.get_model_class())

    def find_obj_by_obj_id(self, input_id) -> ModelLike | None:
        return self.get_model_class().objects.filter(pk=input_id).first()

    def get_obj_desc_list(self, obj) -> list[str]:
        """ description for display about the object to be deleted """
        return [(obj and obj.pk) or 'unknown']

    def get(self, request, obj_id, *args, **kwargs):
        obj = self.find_obj_by_obj_id(obj_id)
        return render(request, 'core/delete_confirm.html', {
            'name': self.get_name(),
            'obj_desc_list': self.get_obj_desc_list(obj),
            'cancel_url': reverse(f'{request.resolver_match.app_name}:{VNAME_FULL_FORM}', args=[obj_id]),
        })

    def post(self, request, obj_id, *args, **kwargs):
        obj = self.find_obj_by_obj_id(obj_id)
        obj_name = general_model_utils.get_display_name(obj)
        if not obj:
            return HttpResponseNotFound()
        obj.delete()
        url = reverse(f'{request.resolver_match.app_name}:{VNAME_SEARCH}')
        msg = f'"{obj_name}" deleted successfully'
        msg = urllib.parse.quote(msg)
        return redirect(f'{url}?to_user_messages={msg}')
