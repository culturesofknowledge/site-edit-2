from django.urls import reverse

from person.models import CofkUnionPerson
from siteedit2.utils.log_utils import log_no_url


def get_recref_display_name(person: CofkUnionPerson):
    return person and person.foaf_name


def get_display_name(person: CofkUnionPerson):
    return get_recref_display_name(person)


def get_recref_target_id(person: CofkUnionPerson):
    return person and person.person_id


def get_form_url(iperson_id):
    return reverse('person:full_form', args=[iperson_id])


def get_display_id(person: CofkUnionPerson):
    return person and person.iperson_id


@log_no_url
def get_checked_form_url_by_pk(pk):
    if person := CofkUnionPerson.objects.get(pk=pk):
        return reverse('person:full_form', args=[person.iperson_id])


def role_name_str(person: CofkUnionPerson, delimiter=', ') -> str:
    return delimiter.join(r.role_category_desc for r in person.roles.all())


def get_name_details(person: CofkUnionPerson) -> list[str]:
    name_details = [person.foaf_name]

    if person.skos_altlabel:
        name_details.append(f"~ Synonyms: {person.skos_altlabel}")

    if person.person_aliases:
        name_details.append(f"~ Titles/roles: {person.person_aliases}")

    if (roles := person.roles.all()).exists():
        roles = ', '.join(r.role_category_desc for r in roles)
        name_details.append(f"~ Role types: {roles}")

    return name_details
