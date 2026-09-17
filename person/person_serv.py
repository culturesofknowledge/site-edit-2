import calendar
import collections
import logging
from datetime import date

from django.urls import reverse

from core.constant import DEFAULT_MONTH
from core.helper import recref_serv
from location import location_serv
from manifestation import manif_serv
from person.models import CofkUnionPerson

log = logging.getLogger(__name__)


def _compute_std_date(year, month, day, year2, month2, day2) -> date | None:
    """Derive the sortable date a precomputed *_std-style DateField should hold
    from its granular year/month/day (and, for a range, year2/month2/day2)
    parts. Mirrors work_serv.compute_date_of_work_std's precedence (prefer the
    "to" date of a range when present), adapted to build a real date object
    (person's fields are DateFields, not CharFields with a string sentinel
    default) so blank-day defaults must stay within the target month.
    """
    if year2:
        y = int(year2)
        m = int(month2 or 12)
        d = int(day2 or calendar.monthrange(y, m)[1])
        return date(y, m, d)

    if not year:
        return None

    y = int(year)
    m = int(month or DEFAULT_MONTH)
    d = int(day or calendar.monthrange(y, m)[1])
    return date(y, m, d)


def compute_date_of_birth(person: CofkUnionPerson) -> date | None:
    """Compute the value date_of_birth should hold, derived fresh from the
    person's granular date fields (see _compute_std_date). date_of_birth is a
    separate, precomputed column that PersonSearchView sorts against directly
    - it is not derived automatically on save, so any code that changes the
    date fields (e.g. bulk uploads) must call this and persist the result."""
    return _compute_std_date(person.date_of_birth_year, person.date_of_birth_month, person.date_of_birth_day,
                             person.date_of_birth2_year, person.date_of_birth2_month, person.date_of_birth2_day)


def compute_date_of_death(person: CofkUnionPerson) -> date | None:
    """See compute_date_of_birth."""
    return _compute_std_date(person.date_of_death_year, person.date_of_death_month, person.date_of_death_day,
                             person.date_of_death2_year, person.date_of_death2_month, person.date_of_death2_day)


def compute_flourished(person: CofkUnionPerson) -> date | None:
    """See compute_date_of_birth."""
    return _compute_std_date(person.flourished_year, person.flourished_month, person.flourished_day,
                             person.flourished2_year, person.flourished2_month, person.flourished2_day)


def get_recref_display_name(person: CofkUnionPerson):
    return person and person.to_string()


def get_display_name(person: CofkUnionPerson):
    return get_recref_display_name(person)


def get_display_name_for_other_details(person: CofkUnionPerson):
    if not person:
        return person
    return person.to_string()


def get_recref_target_id(person: CofkUnionPerson):
    return person and person.person_id


def get_form_url(iperson_id):
    return reverse('person:full_form', args=[iperson_id])


def get_display_id(person: CofkUnionPerson):
    return person and person.iperson_id


def get_checked_form_url_by_pk(pk):
    if person := CofkUnionPerson.objects.get(pk=pk):
        return reverse('person:full_form', args=[person.iperson_id])

    log.warning('get form url failed, person not found [%s]', pk)
    return ''


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
         lambda mm: get_display_name_for_other_details(mm.related),
         lambda mm: mm.person,
         lambda mm: get_form_url(mm.related.iperson_id)),

        # person's passive relationships
        (lambda: person.passive_relationships.all(),
         lambda mm: get_display_name_for_other_details(mm.person),
         lambda mm: mm.related,
         lambda mm: get_form_url(mm.person.iperson_id)),

        # locations
        (lambda: person.cofkpersonlocationmap_set.all(),
         lambda mm: location_serv.get_recref_display_name(mm.location),
         lambda mm: CofkUnionPerson,
         lambda mm: location_serv.get_form_url(mm.location.location_id),
         ),

        # manifs
        (lambda: person.cofkmanifpersonmap_set.all(),
         lambda mm: manif_serv.get_recref_display_name(mm.manifestation),
         lambda mm: CofkUnionPerson,
         lambda mm: manif_serv.get_form_url(mm.manifestation),
         ),

        # comments
        (lambda: person.cofkpersoncommentmap_set.all(),
         lambda mm: mm.comment.comment,
         lambda mm: CofkUnionPerson,
         None,),
    ]

    result_map = collections.defaultdict(list)
    for query_fn, name_fn, left_obj_fn, url_fn in query_name_map:
        for mmap in query_fn():
            display_name = recref_serv.get_recref_rel_desc(mmap, left_obj_fn(mmap),
                                                           default_raw_value=True)
            display_str = name_fn(mmap)
            if mmap.from_date and mmap.from_date.year:
                if mmap.to_date and mmap.to_date.year:
                    display_str = f'{mmap.from_date.year}-{mmap.to_date.year}: {display_str}'
                else:
                    display_str = f'From {mmap.from_date.year}: {display_str}'

            if url_fn:
                display_str = encode_display_link(url_fn(mmap), display_str)
            result_map[display_name].append(display_str)

    # add resources
    if _resources := [encode_display_link(r.resource_url, r.resource_name) for r in person.resources.all()]:
        result_map['Related resources'] = _resources

    title_value_list = []
    for title, values in result_map.items():
        values = (f'~{v}' for v in values)
        title = title[0].upper() + title[1:]
        title_value_list.append(f'* {title}{new_line}' + f'{new_line}'.join(values))

    return f'{new_line + new_line}'.join(title_value_list)


def encode_display_link(url, text):
    return f'__@_[{url}]{text}_@__'


class DisplayablePerson(CofkUnionPerson):
    class Meta:
        proxy = True

    def other_details_for_display(self, new_line='\n'):
        return get_display_dict_other_details(self, new_line=new_line)


class SearchResultPerson(DisplayablePerson):
    """
    Some properties or functions used by the search page
    """

    class Meta:
        proxy = True

    def decode_year_range(self, year1, year2, is_range) -> str | None:
        display_year = ''

        if year1 is not None and year2 is not None:
            display_year = f'{year1} to {year2}'
        elif year2 is not None:
            display_year = f'{year2} or before'
        elif year1 is not None:
            display_year = f'{year1}'
            if is_range == 1:
                display_year += ' or after'

        return display_year

    def flourished_year_range(self):
        if year_range := self.decode_year_range(self.flourished_year, self.flourished2_year,
                                                self.flourished_is_range):
            return f'fl. {year_range}'
        return ''

    def birth_year_range(self):
        return self.decode_year_range(self.date_of_birth_year, self.date_of_birth2_year,
                                      self.date_of_birth_is_range)

    def death_year_range(self):
        return self.decode_year_range(self.date_of_death_year, self.date_of_death2_year,
                                      self.date_of_death_is_range)


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
