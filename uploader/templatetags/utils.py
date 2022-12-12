import logging

from django import template
from django.db.models import QuerySet

from core.models import CofkLookupDocumentType
from work.models import CofkCollectWork

register = template.Library()

log = logging.getLogger(__name__)


@register.filter
def filter_by_work(queryset: QuerySet, work: CofkCollectWork):
    """Filters a queryset by work"""
    return queryset.filter(iwork=work).all()


@register.filter
def document_type(doc_type: str):
    """Looks document type description up"""
    return CofkLookupDocumentType.objects.\
        values_list('document_type_desc', flat=True).filter(document_type_code=doc_type).first()


@register.simple_tag(takes_context=True)
def get_location(context, loc_id: int):
    loc = [loc for loc in context['places'] if loc.location_id == loc_id][0]

    if loc.union_location:
        return loc.union_location

    return loc
