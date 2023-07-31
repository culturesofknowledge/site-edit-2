import logging
from typing import List, Union

from django import template
from django.db.models import QuerySet

from core.models import CofkLookupDocumentType
from uploader.models import CofkCollectWork, CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, \
    CofkCollectPersonMentionedInWork, CofkCollectLanguageOfWork, CofkCollectWorkResource, CofkCollectSubjectOfWork

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

@register.simple_tag
def get_people(queryset: Union[QuerySet, List[CofkCollectAuthorOfWork | CofkCollectAddresseeOfWork
                                              | CofkCollectPersonMentionedInWork]]) -> str:
    people = []
    for person in queryset:
        if person.iperson.union_iperson:
            person = person.iperson.union_iperson
            people.append(f'{person.to_string()} [ID: {person.iperson_id}]')
        else:
            p = f'{person.iperson.to_string()} [new]'

            if person.iperson.editors_notes:
                p += f' [editor\'s notes: {person.iperson.editors_notes}]'

            people.append(p)
    return ', '.join(people)


@register.simple_tag
def get_languages(queryset: Union[QuerySet, List[CofkCollectLanguageOfWork]]) -> str:
        return '; '.join([str(l) for l in queryset])


@register.simple_tag
def display_origin(work: CofkCollectWork) -> str:
    if origin := work.origin.first():
        return str(origin)
    elif work.origin_id:
        return f'[ID {work.origin_id}]'

    return ''

@register.simple_tag
def display_destination(work: CofkCollectWork) -> str:
    if destination := work.destination.first():
        return str(destination)
    elif work.destination_id:
        return f'[ID {work.destination_id}]'

    return ''

@register.simple_tag
def display_places_mentioned(work: CofkCollectWork) -> str:
    places_mentioned = []
    for place in work.places_mentioned.all():
        places_mentioned.append(place.location.to_string())

    return '; '.join(sorted(places_mentioned))


@register.simple_tag
def display_resources(queryset: Union[QuerySet, List[CofkCollectWorkResource]]) -> str:
    resources = []
    for r in queryset:
        if r.resource_name and r.resource_url:
            resources.append(f'{r.resource_name}: {r.resource_url}')
        elif r.resource_url:
            resources.append(r.resource_url)
        elif r.resource_name:
            resources.append(r.resource_name)

    return ' '.join(resources)

@register.simple_tag
def display_subjects(queryset: Union[QuerySet, List[CofkCollectSubjectOfWork]]) -> str:
    return ', '.join([s.subject.subject_desc for s in queryset])


def get_location(queryset: QuerySet, loc_id: int):
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