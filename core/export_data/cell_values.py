"""
This module contains the functions to
convert input to required format of cell value
"""
import collections
from collections.abc import Iterable

from django.conf import settings

from cllib import str_utils
from core import constant
from core.helper import general_model_serv
from core.models import CofkUnionComment, CofkUnionResource
from person import person_serv
from person.models import CofkUnionPerson

DELIMITER_SHACKLE = ' ~ '
DELIMITER_SEMICOLON = '; '
DEFAULT_DELIMITER = DELIMITER_SEMICOLON


def common_join_text(text_list: Iterable, delimiter=DEFAULT_DELIMITER) -> str:
    return str_utils.join_str_list(text_list, drop_empty=False, delimiter=delimiter)


def notes(note_list: Iterable[CofkUnionComment]) -> str:
    comments = (n.comment for n in note_list)
    comments = filter(None, comments)
    return common_join_text(comments)


def name_id(objects: Iterable) -> [str, str]:
    objects = list(objects)
    name = (general_model_serv.get_display_name(p) for p in objects)
    name = common_join_text(name)

    id_str = (general_model_serv.get_display_id(p) for p in objects)
    id_str = map(str, id_str)
    id_str = common_join_text(id_str)
    return name, id_str


def editor_url(url_path: str) -> str:
    return '{}{}'.format(settings.EXPORT_ROOT_URL, url_path, )


def resources_id(resource_recref_list) -> str:
    return common_join_text(r.resource_id for r in resource_recref_list)


def resource_str(obj: CofkUnionResource) -> str:
    return f'{obj.resource_url} ({obj.resource_name})'


def resource_str_by_list(resource_list: Iterable[CofkUnionResource]) -> str:
    return common_join_text((resource_str(r) for r in resource_list),
                            delimiter=DELIMITER_SHACKLE)


def simple_datetime(dt) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def year_month_day(year, month, day) -> str:
    year = year or constant.DEFAULT_YEAR
    month = month or constant.DEFAULT_MONTH
    day = day or constant.DEFAULT_DAY
    return f'{year}-{month}-{day}'


def person_roles(obj: CofkUnionPerson) -> str:
    delimiter = '; '
    roles = obj.person_aliases or ''
    roles = roles.strip().replace('\n', delimiter)
    return roles


def person_names_titles_roles(obj: CofkUnionPerson) -> str:
    return ''.join(person_serv.get_name_details(obj))


def person_other_details(obj: CofkUnionPerson, type_name_cache: dict = None) -> str:
    result_map = collections.defaultdict(list)
    for person_map in obj.active_relationships.all():
        result_map[person_map.relationship_type].append(
            person_serv.get_recref_display_name(person_map.related)
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
