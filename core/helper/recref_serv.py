import dataclasses
import logging
import typing
from typing import Callable, Any, Optional
from typing import Type, Iterable

from django.db.models import Model, Q
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.forms import BaseForm

from cllib import inspect_utils
from cllib_django import django_utils
from core.helper import model_serv, query_cache_serv
from core.helper.model_serv import ModelLike
from core.models import Recref, CofkUnionRelationshipType
from core.recref_settings import recref_left_right_list

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
        log.warning(f"create recref fail, target_instance not found "
                    f"-- target_id[{target_id}] parent[{parent_instance}] ")
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


def find_all_recref_class() -> Iterable[Type[RecrefLike]]:
    models = django_utils.all_model_classes()
    recref_class_list = (m for m in models
                         if inspect_utils.issubclass_safe(m, Recref) and m != Recref)
    return recref_class_list


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


def find_bounded_data_list_by_related_model(model) -> Iterable[RecrefBoundedData]:
    return (r for r in find_all_recref_bounded_data()
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


def get_parent_related_field_by_bounded_data(bounded_data, parent_model):
    return get_parent_related_field(*list(bounded_data.pair), parent_model)


def find_recref_list(recref_class, parent_model, parent_field=None) -> Iterable['Recref']:
    if parent_field is None:
        parent_field = model_serv.get_related_field(recref_class, parent_model.__class__)

    if isinstance(parent_field, ForwardManyToOneDescriptor):
        field_name = parent_field.field.name
    else:
        field_name = parent_field.name

    records = recref_class.objects.filter(**{field_name: parent_model})
    return records


def find_recref_list_by_bounded_data(bounded_data, parent_model) -> Iterable['Recref']:
    parent_field, _ = get_parent_related_field_by_bounded_data(bounded_data, parent_model)
    return find_recref_list(bounded_data.recref_class, parent_model, parent_field=parent_field)


def create_q_rel_type(rel_type: str | Iterable, prefix=None) -> Q:
    if isinstance(rel_type, str):
        name = 'relationship_type'
    else:
        name = 'relationship_type__in'
        rel_type = set(rel_type)

    if prefix:
        name = f'{prefix}__{name}'

    return Q(**{name: rel_type})


def prefetch_filter_rel_type(recref_set, rel_types: str | Iterable[str]) -> Iterable:
    if isinstance(rel_types, str):
        rel_types = [rel_types]
    else:
        rel_types = set(rel_types)

    for recref in recref_set.all():
        if recref.relationship_type in rel_types:
            yield recref


def get_all_union_relationship_types() -> list[CofkUnionRelationshipType]:
    return query_cache_serv.load_cache(query_cache_serv.ck_all_union_relationship_types,
                                       lambda: list(CofkUnionRelationshipType.objects.all()))


def find_relationship_type(relationship_code: str) -> CofkUnionRelationshipType | None:
    all_types = get_all_union_relationship_types()
    for relationship_type in all_types:
        if relationship_type.relationship_code == relationship_code:
            return relationship_type
    return None


def get_left_right_rel_obj(recref: Recref)-> tuple[Model, Model]:
    bounded_members = set(get_bounded_members(recref.__class__)[:2])
    bounded_member_fields = {f.field.name for f in bounded_members}
    left_right_field = ((l, r) for rel_type, l, r in recref_left_right_list
                         if recref.relationship_type == rel_type)
    left_right_field = (p for p in left_right_field if set(p) == bounded_member_fields)
    left_right_field: tuple[str, str] = next(left_right_field, None)

    # define left_col, right_col
    if left_right_field is None:
        log.warning(f'left, right column not found, {recref}')
        left_col, right_col = bounded_members
    else:
        col_a, col_b = bounded_members
        left_field_name, _ = left_right_field
        if col_a.field.name == left_field_name:
            left_col, right_col = col_a, col_b
        else:
            left_col, right_col = col_b, col_a

    left_rel_obj = left_col.get_object(recref)
    right_rel_obj = right_col.get_object(recref)
    return left_rel_obj, right_rel_obj


def get_recref_rel_desc(recref: Recref,
                        left_model: 'ModelLike' | Type['ModelLike'],
                        default_raw_value=False) -> str:
    left_rel_obj, _ = get_left_right_rel_obj(recref)
    if isinstance(left_model, Model):
        is_left = left_rel_obj == left_model
    else:
        is_left = isinstance(left_rel_obj, left_model)

    rel_type = find_relationship_type(recref.relationship_type)
    if not rel_type:
        log.warning(f'rel_type not found [{recref.__class__.__name__}][{recref.relationship_type}]')
        return recref.relationship_type if default_raw_value else ''
    return rel_type.desc_left_to_right if is_left else rel_type.desc_right_to_left
