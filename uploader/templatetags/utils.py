import logging
from typing import List, Union

from django import template
from django.db.models import QuerySet

from uploader.models import CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, \
    CofkCollectPersonMentionedInWork, CofkCollectLanguageOfWork, CofkCollectWorkResource, CofkCollectSubjectOfWork

register = template.Library()

log = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def document_type(context, doc_type: str):
    """Looks document type description up"""
    result = [d[1] for d in context['doc_types'] if d[0] == doc_type]

    if result:
        return result[0]


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
def display_place(places: QuerySet) -> str:
    if places:
        return str(places[0])
    return ''


@register.simple_tag
def display_places_mentioned(places: QuerySet) -> str:
    places_mentioned = []
    for place in places:
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
