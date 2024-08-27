import logging
import re
from typing import Iterable

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.utils.safestring import mark_safe

from audit import forms
from audit.forms import AuditSearchFieldset
from audit.models import CofkUnionAuditLiteral
from cllib_django import query_utils
from core import constant
from core.helper import renderer_serv, query_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView
from work.templatetags import work_util_tags

log = logging.getLogger(__name__)


class AuditSearchView(PermissionRequiredMixin, LoginRequiredMixin, DefaultSearchView):
    permission_required = constant.PM_VIEW_AUDIT

    @property
    def entity(self) -> str:
        return 'audit,audits'

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionAuditLiteral.objects.none()

        field_fn_maps = {
                            'table_name': query_utils.create_eq_query,
                            'column_name': query_utils.create_eq_query,
                            'change_type': query_utils.create_eq_query,
                        } | query_serv.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                               'change_timestamp')

        queries = query_serv.create_queries_by_field_fn_maps(self.request_data, field_fn_maps)
        queries.extend(
            query_serv.create_queries_by_lookup_field(self.request_data, [
                'change_user', 'table_name', 'key_value_text', 'key_decode',
                'change_made', 'audit_id',
            ], search_fields_maps={
                'change_made': ['new_column_value', 'old_column_value'],
            })
        )

        return self.create_queryset_by_queries(CofkUnionAuditLiteral, queries)

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        def record_modifier(record: CofkUnionAuditLiteral):
            record.key_decode = display_resources_safe(record.key_decode)
            record.new_column_value = display_resources_safe(record.new_column_value)
            record.old_column_value = display_resources_safe(record.old_column_value)

            record.record_display_key = create_display_key(record)
            return record

        return renderer_serv.create_table_search_results_renderer('audit/search_table_layout.html',
                                                                  record_modifier=record_modifier)

    @property
    def query_fieldset_list(self) -> Iterable:
        request_data = self.request_data.dict()
        return [AuditSearchFieldset(request_data)]

    def get_search_results_context(self, context):
        records = super().get_search_results_context(context)

        def _update(row: CofkUnionAuditLiteral):
            row.column_name = forms.changed_field_choices_dict.get(row.column_name, row.column_name)
            return row

        return map(_update, records)


def display_resources_safe(value: str) -> str:
    if value and 'xxxCofkLinkStartxxx' in value:
        try:
            resources = work_util_tags.display_resources(value)
            resources = replace_old_url(resources)
            resources = mark_safe(resources)
            return resources
        except Exception as e:
            log.debug(str(e))

    return value


def replace_old_url(value: str) -> str:
    results = re.findall(r'(https?://.+?/interface/union.php\?iwork_id=(\d+))', value)
    if results:
        for url, iwork_id in results:
            value = value.replace(url, reverse("work:overview_form", args=[iwork_id]))
    return value


def create_display_key(record: CofkUnionAuditLiteral) -> str:
    if record.table_name == 'cofk_union_work':
        result = f'Work ID {record.key_value_integer}'
    elif record.table_name == 'cofk_union_person':
        result = f'Person ID {record.key_value_integer}'
    elif record.table_name == 'cofk_union_location':
        result = f'Location ID {record.key_value_integer}'
    elif record.table_name == 'cofk_union_institution':
        result = f'Institution ID {record.key_value_integer}'
    elif record.table_name == 'cofk_union_manifestation':
        result = f'Manifestation ID {record.key_value_text}'
    elif record.table_name == 'cofk_union_comment':
        result = f'Comment ID {record.key_value_text}'
    elif record.table_name == 'cofk_union_resource':
        result = f'Resource ID {record.key_value_text}'
    else:
        result = record.key_value_text

    return result
