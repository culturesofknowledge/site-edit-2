import datetime
import functools
import logging
from typing import Iterable

import django
from django.conf import settings
from django.db.models import Q


class RecordTracker:

    def update_current_user_timestamp(self, user):
        now = datetime.datetime.now()
        if hasattr(self, 'creation_timestamp') and not self.creation_timestamp:
            self.creation_timestamp = now

        if hasattr(self, 'change_timestamp'):
            self.change_timestamp = now

        if hasattr(self, 'creation_user') and not self.creation_user:
            self.creation_user = user

        if hasattr(self, 'change_user'):
            self.change_user = user


def create_lookup_query(field, lookup, value) -> Q:
    return Q(**{f'{field}__{lookup}': value})


def create_contains_query(field, value) -> Q:
    return create_lookup_query(field, 'contains', value)


def create_eq_query(field, value):
    return Q(**{field: value})


def any_queries(queries: Iterable[Q]):
    return functools.reduce(lambda a, b: a | b, queries, Q())


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
    return datetime.datetime.now()
