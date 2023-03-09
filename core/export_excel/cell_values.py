"""
This module contains the functions to
convert input to required format of cell value
"""
from collections.abc import Iterable

from django.conf import settings

from core.helper import general_model_utils
from core.models import CofkUnionComment


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


def simple_datetime(dt) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')
