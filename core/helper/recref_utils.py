import logging
from typing import Callable, Any

log = logging.getLogger(__name__)


def convert_to_recref_form_dict(record_dict: dict, target_id_name: str,
                                find_rec_name_by_id_fn: Callable[[Any], str]) -> dict:
    target_id = record_dict.get(target_id_name, '')
    record_dict['target_id'] = target_id
    if (rec_name := find_rec_name_by_id_fn(target_id)) is None:
        log.warning(f"[{target_id_name}] record not found -- [{target_id}]")
    else:
        record_dict['rec_name'] = rec_name

    return record_dict
