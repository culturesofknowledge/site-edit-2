import functools
from typing import Iterable

from django.db.models import Q, F, Lookup


def create_lookup_query(field, lookup, value) -> Q:
    return Q(**{f'{field}__{lookup}': value})


def create_contains_query(field, value) -> Q:
    return create_lookup_query(field, 'contains', value)


def create_eq_query(field, value) -> Q:
    return Q(**{field: value})


def create_query_factory_by_lookup(lookup):
    def _query_factory(field, value):
        return lookup(F(field), value)

    return _query_factory


def any_queries_match(queries: Iterable[Q]) -> Q:
    return functools.reduce(lambda a, b: a | b, queries, Q())


def all_queries_match(queries: Iterable[Q]) -> Q:
    return functools.reduce(lambda a, b: a & b, queries, Q())


def create_queries_by_field_fn_maps(field_fn_maps: dict, data: dict) -> list[Q]:
    def _run_fn(_fn, _field, _val):
        if issubclass(_fn, Lookup):
            _field = F(_field)
        return _fn(_field, _val)

    query_field_values = ((f, data.get(f)) for f in field_fn_maps.keys())
    query_field_values = ((f, v) for f, v in query_field_values if v)
    queries = [_run_fn(field_fn_maps[f], f, v) for f, v in query_field_values]
    return queries
