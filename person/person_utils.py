import collections

from django.urls import reverse

from core.helper import recref_utils
from location import location_utils
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


def get_display_dict_other_details(person: CofkUnionPerson, new_line='\n') -> str:
    query_name_map = [
        # locations
        (lambda: person.cofkpersonlocationmap_set.all(),
         lambda model_map: location_utils.get_recref_display_name(model_map.location),),

        # comments
        (lambda: person.cofkpersoncommentmap_set.all(),
         lambda model_map: model_map.comment.comment,),
    ]

    result_map = collections.defaultdict(list)

    # persons
    for mmap in person.active_relationships.all():
        display_name = recref_utils.get_recref_rel_desc(mmap, mmap.person, default_raw_value=True)
        result_map[display_name].append(
            get_recref_display_name(mmap.related)
        )

    for query_fn, name_fn in query_name_map:
        for mmap in query_fn():
            display_name = recref_utils.get_recref_rel_desc(mmap, CofkUnionPerson, default_raw_value=True)
            result_map[display_name].append(
                name_fn(mmap)
            )

    # add resources
    if _resources := [f'{r.resource_url} ({r.resource_name})' for r in person.resources.all()]:
        result_map['Related resources'] = _resources

    title_value_list = []
    for title, values in result_map.items():
        values = (f'~{v}' for v in values)
        title = title[0].upper() + title[1:]
        title_value_list.append(f'* {title}{new_line}' + f'{new_line}'.join(values))

    return f'{new_line + new_line}'.join(title_value_list)


class DisplayablePerson(CofkUnionPerson):
    class Meta:
        proxy = True

    def other_details_for_display(self, new_line='\n'):
        return get_display_dict_other_details(self, new_line=new_line)
