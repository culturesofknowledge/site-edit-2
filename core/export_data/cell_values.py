"""
This module contains the functions to
convert input to required format of cell value
"""
from collections.abc import Iterable

from django.conf import settings

from core.helper import general_model_utils
from core.models import CofkUnionComment, CofkUnionResource
from person import person_utils
from person.models import CofkUnionPerson
import collections


def common_join_text(text_list: Iterable, delimiter='; ') -> str:
    text_list = map(str, text_list)
    return delimiter.join(text_list)


def notes(note_list: Iterable[CofkUnionComment]) -> str:
    comments = (n.comment for n in note_list)
    comments = filter(None, comments)
    return common_join_text(comments)


def name_id(objects: Iterable) -> [str, str]:
    objects = list(objects)
    name = (general_model_utils.get_display_name(p) for p in objects)
    name = common_join_text(name)

    id_str = (general_model_utils.get_display_id(p) for p in objects)
    id_str = map(str, id_str)
    id_str = common_join_text(id_str)
    return name, id_str


def editor_url(url_path: str) -> str:
    return '{}{}'.format(settings.EXPORT_ROOT_URL, url_path, )


def resources_id(resource_recref_list) -> str:
    return common_join_text(r.resource_id for r in resource_recref_list)


def resource_str(obj: CofkUnionResource) -> str:
    return f'{obj.resource_url} ({obj.resource_name})'


def simple_datetime(dt) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def year_month_day(year, month, day) -> str:
    if year and not month and not day:
        return str(year)

    if not year and not month and not day:
        return ''

    return f'{year}-{month}-{day}'


def person_roles(obj: CofkUnionPerson) -> str:
    return person_utils.role_name_str(obj)


def person_names_titles_roles(obj: CofkUnionPerson) -> str:
    join_list = []
    if obj.foaf_name:
        join_list.append(obj.foaf_name)

    if obj.person_aliases:
        join_list.append(obj.person_aliases)

    if role := person_roles(obj):
        join_list.append(role)

    return ' ~ '.join(join_list)


def person_other_details(obj: CofkUnionPerson, type_name_cache: dict = None) -> str:
    result_map = collections.defaultdict(list)
    for person_map in obj.active_relationships.all():
        result_map[person_map.relationship_type].append(
            person_utils.get_recref_display_name(person_map.related)
        )

    if type_name_cache:
        keys = [k for k in result_map.keys() if k in type_name_cache]
        for k in keys:
            result_map[type_name_cache[k]] = result_map[k]
            del result_map[k]

    # add resources
    if _resources := [resource_str(r) for r in obj.resources.all()]:
        result_map['Related resources'] = _resources

    title_value_list = []
    for title, values in result_map.items():
        values = (f'~{v}' for v in values)
        title = title[0].upper() + title[1:]
        title_value_list.append(f'*{title}\n' + '\n'.join(values))

    return '\n\n'.join(title_value_list)


def person_org_type(obj: CofkUnionPerson) -> str:
    org_type = obj.organisation_type
    org_type = org_type.org_type_desc if org_type else ''
    return org_type
