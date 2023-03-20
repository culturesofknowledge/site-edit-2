from typing import Callable, Iterable

from django.contrib.auth.mixins import LoginRequiredMixin

from audit import forms
from audit.forms import AuditSearchFieldset
from audit.models import CofkUnionAuditLiteral
from core.helper import renderer_utils, query_utils
from core.helper.date_utils import str_to_search_datetime
from core.helper.view_utils import DefaultSearchView


class AuditSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def entity(self) -> str:
        return 'audit,audits'

    @property
    def search_page_vname(self) -> str:
        return 'audit:search'

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionAuditLiteral.objects.none()

        field_fn_maps = {
                            'table_name': query_utils.create_eq_query,
                            'column_name': query_utils.create_eq_query,
                            'change_type': query_utils.create_eq_query,
                        } | query_utils.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                                'change_timestamp')

        queries = query_utils.create_queries_by_field_fn_maps(field_fn_maps, self.request_data)
        queries.extend(
            query_utils.create_queries_by_lookup_field(self.request_data, [
                'change_user', 'table_name', 'key_value_text', 'key_decode',
                'change_made', 'audit_id',
            ], search_fields_maps={
                'change_made': ['new_column_value', 'old_column_value'],
            })
        )

        return self.create_queryset_by_queries(CofkUnionAuditLiteral, queries)

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('audit/search_table_layout.html')

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
