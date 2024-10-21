import itertools
import logging
from typing import Iterable, Type, TYPE_CHECKING

from django.db.models import ForeignKey

from cllib import inspect_utils
from cllib_django import django_utils
from core.helper import recref_serv, general_model_serv
from core.helper.model_serv import ModelLike
from core.models import MergeHistory

if TYPE_CHECKING:
    from core.models import Recref

log = logging.getLogger(__name__)


def find_related_collect_field(target_model_class: Type[ModelLike]) -> Iterable[tuple[Type[ModelLike], ForeignKey]]:
    def _is_target_field(f):
        return isinstance(f, ForeignKey) and inspect_utils.issubclass_safe(f.related_model, target_model_class)

    _models = django_utils.all_model_classes()
    _models = (m for m in _models if m.__name__.startswith('CofkCollect'))
    _models = itertools.chain.from_iterable(
        ((m, f) for f in m._meta.fields if _is_target_field(f))
        for m in _models)
    return _models


def merge(selected_model: ModelLike, other_models: list[ModelLike], username=None):
    if selected_model and len(other_models) == 0:
        msg = f'invalid selected_model[{selected_model}], empty other_models[{len(other_models)}] '
        log.warning(msg)
        return ValueError(msg)

    log.info('merge type[{}] selected[{}] other[{}]'.format(
        selected_model.__class__.__name__,
        selected_model.pk,
        [m.pk for m in other_models]
    ))

    recref_list: Iterable[Recref] = recref_serv.find_all_recref_by_models(other_models)
    recref_list = list(recref_list)
    for recref in recref_list:
        parent_field, _ = recref_serv.get_parent_related_field_by_recref(recref, selected_model)

        # update related_field on recref
        related_field_name = parent_field.field.name
        log.debug(f'change related record. [{recref.__class__.__name__}] recref[{recref.pk}]'
                  f' related_name[{related_field_name}]'
                  f' from[{getattr(recref, related_field_name).pk}] to[{selected_model.pk}]')
        setattr(recref, related_field_name, selected_model)
        if username:
            recref.update_current_user_timestamp(username)
        recref.save()

    # TODO no longer needed update cofk_collect if Emlo Collector removed
    # change ForeignKey value to master's id in cofk_collect
    for model_class, foreign_field in find_related_collect_field(selected_model.__class__):
        new_id = foreign_field.target_field.value_from_object(selected_model)
        old_ids = [foreign_field.target_field.value_from_object(o) for o in other_models]
        outdated_records = model_class.objects.filter(**{
            f'{foreign_field.attname}__in': old_ids
        })
        log.info('update [{}.{}] with old_ids[{}] to new_id[{}], total[{}]'.format(
            model_class.__name__, foreign_field.attname,
            old_ids, new_id, outdated_records.count()
        ))
        outdated_records.update(**{foreign_field.attname: new_id})

    # add merge history
    for old_model in other_models:
        merge_history = MergeHistory.objects.create(
            new_id=str(selected_model.pk),
            new_name=general_model_serv.get_display_name(selected_model),
            new_display_id=general_model_serv.get_display_id(selected_model),
            old_id=str(old_model.pk),
            old_name=general_model_serv.get_display_name(old_model),
            old_display_id=general_model_serv.get_display_id(old_model),
            model_class_name=selected_model.__class__.__name__,
        )
        if username:
            merge_history.update_current_user_timestamp(username)
        merge_history.save()

    return recref_list
