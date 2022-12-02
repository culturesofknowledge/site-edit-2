from typing import Callable, Iterable

from django.contrib.auth.mixins import LoginRequiredMixin

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
