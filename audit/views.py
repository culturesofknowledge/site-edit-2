from typing import Callable, Iterable

from django.contrib.auth.mixins import LoginRequiredMixin

from audit import forms
from audit.forms import AuditSearchFieldset
from audit.models import CofkUnionAuditLiteral
from core.helper import renderer_utils
from core.helper.view_utils import DefaultSearchView


class AuditSearchView(LoginRequiredMixin, DefaultSearchView):

    def get_queryset(self):
        queryset = CofkUnionAuditLiteral.objects.all()
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('audit/search_table_layout.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        default_values = {
            'foaf_name_lookup': 'starts_with',
        }
        request_data = default_values | self.request_data.dict()

        return [AuditSearchFieldset(request_data)]

    def get_search_results_context(self, context):
        records = super().get_search_results_context(context)

        def _update(row: CofkUnionAuditLiteral):
            row.column_name = forms.changed_field_choices_dict.get(row.column_name, row.column_name)
            return row

        return map(_update, records)
