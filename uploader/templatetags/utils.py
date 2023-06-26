from django import template
from django.db.models import QuerySet

from core.models import CofkLookupDocumentType
from uploader.models import CofkCollectWork

register = template.Library()

@register.filter
def filter_by_work(queryset: QuerySet, work: CofkCollectWork):
    """Filters a queryset by work"""
    return queryset.filter(iwork=work).all()


@register.filter
def document_type(doc_type: str):
    """Looks document type description up"""
    return CofkLookupDocumentType.objects.\
        values_list('document_type_desc', flat=True).filter(document_type_code=doc_type).first()


def get_location(queryset, loc_id: int):
    loc = [loc for loc in queryset if loc.location.location_id == loc_id][0]

    if loc.location.union_location:
        return loc.location.union_location

    return loc.location

@register.simple_tag(takes_context=True)
def get_origin(context, loc_id: int):
    return get_location(context['origins'], loc_id)

@register.simple_tag(takes_context=True)
def get_destination(context, loc_id: int):
    return get_location(context['destinations'], loc_id)