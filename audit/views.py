from typing import Iterable

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from audit import forms
from audit.forms import AuditSearchFieldset
from audit.models import CofkUnionAuditLiteral
from core import constant
from core.helper import renderer_serv, query_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView


class AuditSearchView(PermissionRequiredMixin, LoginRequiredMixin, DefaultSearchView):
    permission_required = constant.PM_VIEW_AUDIT

    @property
    def entity(self) -> str:
        return 'audit,audits'

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionAuditLiteral.objects.none()

        field_fn_maps = {
                            'table_name': query_serv.create_eq_query,
                            'column_name': query_serv.create_eq_query,
                            'change_type': query_serv.create_eq_query,
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
        return renderer_serv.create_table_search_results_renderer('audit/search_table_layout.html')

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
