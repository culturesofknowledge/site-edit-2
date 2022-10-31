import logging
from typing import Callable, Any, Optional

from core.models import Recref

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


def upsert_recref(rel_type, parent_instance, target_instance,
                  create_recref_fn,
                  set_parent_target_instance_fn,
                  username=None,
                  org_recref=None,
                  ) -> Recref:
    recref = org_recref or create_recref_fn()
    set_parent_target_instance_fn(recref, parent_instance, target_instance)
    recref.relationship_type = rel_type
    if username:
        recref.update_current_user_timestamp(username)
    return recref


def upsert_recref_by_target_id(target_id,
                               find_target_fn,
                               rel_type, parent_instance,
                               create_recref_fn,
                               set_parent_target_instance_fn,
                               username=None,
                               org_recref=None, ) -> Optional[Recref]:
    if not (target_instance := find_target_fn(target_id)):
        log.warning(f"create recref fail, target_instance not found -- {target_id} ")
        return None

    return upsert_recref(
        rel_type, parent_instance, target_instance,
        create_recref_fn=create_recref_fn,
        set_parent_target_instance_fn=set_parent_target_instance_fn,
        username=username,
        org_recref=org_recref,
    )
