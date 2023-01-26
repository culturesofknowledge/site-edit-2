import dataclasses
import logging
from typing import Callable, Any, Optional

import typing
from typing import Type, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from core.helper.model_utils import ModelLike

from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.forms import BaseForm

from core.helper import inspect_utils, django_utils
from core.models import Recref

log = logging.getLogger(__name__)

RecrefLike = typing.TypeVar('RecrefLike', bound=Recref)


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


def create_recref_if_field_exist(form: BaseForm, parent, username,
                                 selected_id_field_name,
                                 rel_type,
                                 recref_adapter: 'RecrefFormAdapter',
                                 ):
    if not (_id := form.cleaned_data.get(selected_id_field_name)):
        return

    target = recref_adapter.find_target_instance(_id)
    recref = recref_adapter.upsert_recref(rel_type,
                                          parent_instance=parent,
                                          target_instance=target,
                                          username=username)
    recref.save()
    log.info(f'add new [{target}][{recref}]')
    return recref


def fill_common_recref_field(recref: Recref, cleaned_data: dict, username):
    recref.to_date = cleaned_data.get('to_date')
    recref.from_date = cleaned_data.get('from_date')
    recref.update_current_user_timestamp(username)
    return recref


@dataclasses.dataclass
class RecrefBoundedData:
    recref_class: Type[RecrefLike]
    pair: list[ForwardManyToOneDescriptor]

    @property
    def pair_related_models(self) -> Iterable[Type['ModelLike']]:
        return (m.field.related_model for m in self.pair)


def get_bounded_members(recref_class: Type[RecrefLike]) -> list[ForwardManyToOneDescriptor]:
    bounded_members = recref_class.__dict__.items()
    bounded_members = (m for n, m in bounded_members
                       if isinstance(m, ForwardManyToOneDescriptor))
    bounded_members = list(bounded_members)
    if len(bounded_members) != 2:
        log.warning('unexpected number of bounded members'
                    f' [{len(bounded_members)}][{recref_class}][{bounded_members}]')
    return bounded_members


def find_all_recref_bounded_data(models: Iterable[Type['ModelLike']] = None) -> Iterable[RecrefBoundedData]:
    models = models or django_utils.all_model_classes()
    recref_class_list = (m for m in models
                         if inspect_utils.issubclass_safe(m, Recref) and m != Recref)

    for recref_class in recref_class_list:
        bounded_members = get_bounded_members(recref_class)
        if len(bounded_members) != 2:
            continue

        bounded_data = RecrefBoundedData(recref_class=recref_class,
                                         pair=bounded_members)
        yield bounded_data


all_recref_bounded_data: list[RecrefBoundedData] = list(find_all_recref_bounded_data(django_utils.all_model_classes()))


def find_bounded_data_list_by_related_model(model) -> Iterable[RecrefBoundedData]:
    return (r for r in all_recref_bounded_data
            if model.__class__ in set(r.pair_related_models))


def get_parent_related_field(field_a: 'ForwardManyToOneDescriptor',
                             field_b: 'ForwardManyToOneDescriptor',
                             parent_model: 'ModelLike',
                             ) -> tuple['ForwardManyToOneDescriptor', 'ForwardManyToOneDescriptor']:
    if field_a.field.related_model == parent_model.__class__:
        parent_field = field_a
        related_field = field_b
    else:
        parent_field = field_b
        related_field = field_a
    return parent_field, related_field


def get_parent_related_field_by_recref(recref: Recref,
                                       parent_model: 'ModelLike',
                                       ) -> tuple['ForwardManyToOneDescriptor', 'ForwardManyToOneDescriptor']:
    return get_parent_related_field(*get_bounded_members(recref.__class__)[:2], parent_model)


def find_recref_list_by_bounded_data(bounded_data, parent_model) -> Iterable['Recref']:
    parent_field, _ = get_parent_related_field(bounded_data, parent_model)
    records = bounded_data.recref_class.objects.filter(**{parent_field.field.name: parent_model})
    return records
