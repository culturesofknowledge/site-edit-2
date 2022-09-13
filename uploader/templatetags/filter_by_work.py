import logging

from django import template
from django.db.models import QuerySet

from work.models import CofkCollectWork

register = template.Library()

log = logging.getLogger(__name__)


@register.filter(name='filter_by_work')
def filter_by_work(queryset: QuerySet, work: CofkCollectWork):
    """Filters a queryset by work"""
    return queryset.filter(iwork=work).all()
