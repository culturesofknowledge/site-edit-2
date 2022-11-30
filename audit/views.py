from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from audit.models import CofkUnionAuditLiteral
from core.helper.view_utils import BasicSearchView, DefaultSearchView


class AuditSearchView(LoginRequiredMixin, DefaultSearchView):

    def get_queryset(self):
        queryset = CofkUnionAuditLiteral.objects.all()
        return queryset
