import collections

from django.urls import reverse

from core.helper import recref_serv
from location import location_serv
from person.models import CofkUnionPerson
from siteedit2.serv.log_serv import log_no_url


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
        # person's active relationships
        (lambda: person.active_relationships.all(),
         lambda mm: get_recref_display_name(mm.related),
         lambda mm: mm.person,),

        # person's passive relationships
        (lambda: person.passive_relationships.all(),
         lambda mm: get_recref_display_name(mm.person),
         lambda mm: mm.related,),

        # locations
        (lambda: person.cofkpersonlocationmap_set.all(),
         lambda mm: location_serv.get_recref_display_name(mm.location),
         lambda mm: CofkUnionPerson,),

        # comments
        (lambda: person.cofkpersoncommentmap_set.all(),
         lambda mm: mm.comment.comment,
         lambda mm: CofkUnionPerson,),
    ]

    result_map = collections.defaultdict(list)
    for query_fn, name_fn, left_obj_fn in query_name_map:
        for mmap in query_fn():
            display_name = recref_serv.get_recref_rel_desc(mmap, left_obj_fn(mmap),
                                                           default_raw_value=True)
            result_map[display_name].append(name_fn(mmap))

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

    def flourished_for_display(self) -> str:
        if self.flourished_year and self.flourished2_year:
            return f'{self.flourished_year} to {self.flourished2_year}'
        elif self.flourished_year and self.flourished_is_range:
            return f'{self.flourished_year} or after'
        elif self.flourished2_year and self.flourished_is_range:
            return f'{self.flourished2_year} or before'
        elif self.flourished_year:
            return self.flourished_year


def decode_is_range_year(year1, year2, is_range):
    if year2 is not None:
        display_year = f'{year2} or before'
    else:
        display_year = f'{year1}'
        if is_range == 1:
            display_year += ' or after'

    return display_year


def decode_person_birth(person: CofkUnionPerson):
    return decode_is_range_year(person.date_of_birth_year, person.date_of_birth2_year,
                                person.date_of_birth_is_range)


def decode_person_death(person: CofkUnionPerson):
    return decode_is_range_year(person.date_of_death_year, person.date_of_death2_year,
                                person.date_of_death_is_range)


def decode_person(person: CofkUnionPerson, is_expand_details=False, ):
    decode = person.foaf_name.strip()

    # organisation
    if person.is_organisation and (org_type := person.organisation_type):
        decode += f' ({org_type.org_type_desc})'

    # Both birth and death dates known
    if (
            (person.date_of_birth_year is not None or person.date_of_birth2_year is not None)
            and (person.date_of_death_year is not None or person.date_of_death2_year is not None)
    ):
        birth_decode = decode_person_birth(person)
        death_decode = decode_person_death(person)
        decode += f', {birth_decode}-{death_decode}'
    elif person.date_of_birth_year is not None or person.date_of_birth2_year is not None:
        # Only birthdate known
        connect_label = ', formed ' if person.is_organisation == 'Y' else ', b.'
        decode += f'{connect_label}{decode_person_birth(person)}'
    elif person.date_of_death_year is not None or person.date_of_death2_year is not None:
        connect_label = ', disbanded ' if person.is_organisation == 'Y' else ', d.'
        decode += f'{connect_label}{decode_person_death(person)}'

    # Flourished dates known
    if person.flourished_year is not None or person.flourished2_year is not None:
        connect_label = ', fl. '

        if person.flourished_year is not None and person.flourished2_year is not None:
            decode += f'{connect_label}{person.flourished_year}-{person.flourished2_year}'
        elif person.flourished_year is not None:
            decode += f'{connect_label}{person.flourished_year}'
            if person.flourished_is_range == 1:
                decode += ' and after'
        elif person.flourished2_year:
            decode += f'{connect_label} until {person.flourished2_year}'

    # Add alternative names?
    if is_expand_details and person.skos_altlabel:
        decode += '; alternative name(s): ' + person.skos_altlabel

    return decode
