import logging
import typing
import uuid
from typing import Iterable, Type, Optional

import django
import django.utils.timezone
from django.conf import settings
from django.db import models
from django.db.models import Model, Max, ForeignKey

ModelLike = typing.TypeVar('ModelLike', bound=models.Model)
ModelOrClass = ModelLike | Type[ModelLike]


def get_table_name(model) -> str:
    return model._meta.db_table

class RecordTracker:

    def update_current_user_timestamp(self, user):
        now = default_current_timestamp()
        if hasattr(self, 'creation_timestamp') and not self.creation_timestamp:
            self.creation_timestamp = now

        if hasattr(self, 'creation_user') and not self.creation_user:
            self.creation_user = user

            # it must be a new record, so creation_timestamp must be set
            if hasattr(self, 'creation_timestamp'):
                self.creation_timestamp = now

        if hasattr(self, 'change_timestamp'):
            self.change_timestamp = now

        if hasattr(self, 'change_user'):
            self.change_user = user


def next_seq_safe(seq_name):
    from django.db import connection

    cursor = connection.cursor()
    nextval_sql = f"select nextval('{seq_name}')"
    try:
        cursor.execute(nextval_sql)
    except django.db.utils.ProgrammingError as e:
        if f'"{seq_name}" does not exist' not in str(e):
            raise e

        init_val = settings.EMLO_SEQ_VAL_INIT.get(seq_name, None)
        if init_val is None:
            logging.debug(f'init val of [{seq_name}] not found in EMLO_SEQ_VAL_INIT')
            init_val = 1

        cursor.execute(f"CREATE SEQUENCE {seq_name} start with {init_val} ")
        cursor.execute(nextval_sql)

    result = cursor.fetchone()
    return result[0]


def default_current_timestamp():
    return django.utils.timezone.now()


def default_uuid():
    return str(uuid.uuid4())


def related_manager_to_dict_list(related_manager) -> Iterable[dict]:
    return models_to_dict_list(related_manager.iterator())


def models_to_dict_list(model_list) -> Iterable[dict]:
    return (r.__dict__ for r in model_list)


def create_multi_records_by_dict_list(model_class: Type[models.Model],
                                      dict_list: Iterable[dict]) -> list:
    records = [model_class(**r) for r in dict_list]
    model_class.objects.bulk_create(records)
    return records


def get_safe(model_class: Type[Model], **kwargs) -> Optional[Model]:
    return model_class.objects.filter(**kwargs).first()


def get_or_create(model_class: Type[Model], **field_values) -> Model:
    if obj := get_safe(model_class, **field_values):
        return obj

    return model_class(**field_values)


def find_max_id(model: Type[ModelLike], field_name: str):
    return list(model.objects.aggregate(Max(field_name)).values())[0]


def get_related_field(model_class: Type[ModelLike], target_class: Type[ModelLike]) -> ForeignKey | None:
    for f in model_class._meta.fields:
        if f.related_model == target_class:
            return f
    return None


class UniqueModelPkFilter:
    def __init__(self, model_list: Iterable[ModelLike]):
        self.pk_list = set()
        self.model_list = model_list

    def __iter__(self):
        self.pk_list = set()
        for model in self.model_list:
            if model.pk not in self.pk_list:
                self.pk_list.add(model.pk)
                yield model
