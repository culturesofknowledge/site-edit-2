import logging
from typing import Iterable, Type

import django
from django.conf import settings
import django.utils.timezone
from django.db import models


class RecordTracker:

    def update_current_user_timestamp(self, user):
        now = default_current_timestamp()
        if hasattr(self, 'creation_timestamp') and not self.creation_timestamp:
            self.creation_timestamp = now

        if hasattr(self, 'change_timestamp'):
            self.change_timestamp = now

        if hasattr(self, 'creation_user') and not self.creation_user:
            self.creation_user = user

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


def related_manager_to_dict_list(related_manager) -> Iterable[dict]:
    return (r.__dict__ for r in related_manager.iterator())


def create_multi_records_by_dict_list(model_class: Type[models.Model],
                                      dict_list: Iterable[dict]) -> list:
    records = [model_class(**r) for r in dict_list]
    model_class.objects.bulk_create(records)
    return records
