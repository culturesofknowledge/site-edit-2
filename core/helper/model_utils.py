import datetime
import functools
from typing import Iterable

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
