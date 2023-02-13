import dataclasses
import itertools
import logging
import os
from collections import defaultdict
from multiprocessing import Process
from typing import Iterable, Type, Callable, Any, TYPE_CHECKING
from typing import NoReturn
from urllib.parse import urlencode

from django import template
from django.db import models
from django.db.models import Q, ForeignKey
from django.db.models.query_utils import DeferredAttribute
from django.forms import ModelForm
from django.forms import formset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

import core.constant as core_constant
from core import constant
from core.forms import build_search_components
from core.helper import file_utils, email_utils, query_utils, general_model_utils, recref_utils, model_utils, \
    django_utils, inspect_utils
from core.helper.model_utils import ModelLike, RecordTracker
from core.helper.renderer_utils import CompactSearchResultsRenderer, DemoCompactSearchResultsRenderer, \
    demo_table_search_results_renderer
from core.helper.view_components import DownloadCsvHandler
from core.models import CofkUnionResource, CofkUnionComment
from work import work_utils
from work.models import CofkUnionWork

if TYPE_CHECKING:
    from core.models import Recref

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
    def search_fields(self) -> list[str]:
        """
        returns a list of all the standard model fields to search on.
        """
        raise NotImplementedError()

    def search_field_label_map(self) -> dict:
        """
        A dictionary mapping between the model field name and the labelling of that field.

        Only used by self.simplified_query.
        """
        raise NotImplementedError()

    @property
    def search_field_fn_maps(self) -> dict:
        """
        A dictionary mapping between form field names where there is more than one field to search against
        simultaneously, such as with ranges.

        Used with query_utils.create_queries_by_field_fn_maps and query_utils.create_from_to_datetime for instance.
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
                    field_name in self.request_data and 'blank' in self.request_data.get(f'{field_name}_lookup')):
                label_name = self.search_field_label_map[field_name]
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
                        'simplified_query': self.simplified_query
                        })
        if self.merge_page_vname:
            context['merge_page_url'] = reverse(self.merge_page_vname)

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
    def search_fields(self) -> list[str]:
        """
        return
        """
        return []

    @property
    def search_field_fn_maps(self) -> dict:
        """
        return
        """
        return {}

    @property
    def search_field_label_map(self) -> dict:
        """
        return
        """
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
    if isinstance(related_model, (CofkUnionComment, CofkUnionResource)):
        return '[{}] {}'.format(
            related_model.pk,
            general_model_utils.get_display_name(related_model)
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


class MergeActionViews(View):
    @property
    def target_model_class(self) -> Type[ModelLike]:
        raise NotImplementedError()

    @property
    def return_vname(self) -> str:
        """ vname for return button """
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

        # update query work if needed
        for work in find_work_by_recref_list(recref_list):
            work_utils.clone_queryable_work(work)

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

    def post(self, request, *args, **kwargs):
        selected_pk = request.POST.get('selected_pk')
        merge_pk_list = set(request.POST.getlist('merge_pk')) - {selected_pk}
        other_models = list(self.target_model_class.objects.filter(**{'pk__in': merge_pk_list}).iterator())
        selected_model = self.target_model_class.objects.filter(**{'pk': selected_pk}).first()

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
            'return_vname': self.return_vname,
            'name': general_model_utils.get_display_name(selected_model),
        })
