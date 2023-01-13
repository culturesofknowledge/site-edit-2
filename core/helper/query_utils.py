import functools
import logging
from typing import Callable, Iterable, Union

from django.db.models import F
from django.db.models import Q, Lookup, lookups
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual

from core.helper import date_utils

log = logging.getLogger(__name__)


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


def run_lookup_fn(_fn, _field, _val):
    if (isinstance(_fn, type)
            and issubclass(_fn, Lookup)
            and not isinstance(_field, F)):
        _field = F(_field)

    return _fn(_field, _val)


def create_queries_by_field_fn_maps(field_fn_maps: dict, data: dict) -> list[Q]:
    query_field_values = ((f, data.get(f)) for f in field_fn_maps.keys())
    query_field_values = ((f, v) for f, v in query_field_values if v)
    queries = [run_lookup_fn(field_fn_maps[f], f, v)
               for f, v in query_field_values]
    return queries


def create_queries_by_lookup_field(request_data: dict,
                                   search_field_names: Union[list[str]],
                                   search_fields_maps: dict[str, Iterable[str]] = None
                                   ) -> Iterable[Q]:
    for field_name in search_field_names:
        field_val = request_data.get(field_name)
        lookup_key = request_data.get(f'{field_name}_lookup')

        if not field_val and lookup_key not in nullable_lookup_keys:
            continue

        if (lookup_fn := choices_lookup_map.get(lookup_key)) is None:
            log.warning(f'lookup fn not found -- [{field_name}][{lookup_key}]')
            continue

        if field_name in search_fields_maps:
            q = Q()
            for search_field in search_fields_maps[field_name]:
                q.add(run_lookup_fn(lookup_fn, search_field, field_val), Q.OR)
            yield q
        else:
            yield run_lookup_fn(lookup_fn, field_name, field_val)


def cond_not(lookup_fn: Callable) -> Callable:
    def _fn(field, val):
        q = lookup_fn(F(field), val)
        if not isinstance(q, Q):
            q = Q(q)
        return ~q

    return _fn


def is_blank(field, val) -> Callable:
    if not isinstance(field, F):
        field = F(field)
    return lookups.IsNull(field, True) | lookups.Exact(field, '')


choices_lookup_map = {
    'contains': lookups.IContains,
    'starts_with': lookups.IStartsWith,
    'ends_with': lookups.IEndsWith,
    'equals': lookups.IExact,
    'not_contain': cond_not(lookups.IContains),
    'not_start_with': cond_not(lookups.IStartsWith),
    'not_end_with': cond_not(lookups.IEndsWith),
    'not_equal_to': cond_not(lookups.IExact),
    'is_blank': is_blank,
    'not_blank': cond_not(is_blank),
    'less_than': lookups.LessThan,
    'greater_than': lookups.GreaterThan,
    None: lookups.Exact,
    '': lookups.Exact,
}

nullable_lookup_keys = [
    'is_blank', 'not_blank',
]


def create_from_to_datetime(from_field_name, to_field_name, db_field_name):
    return {
        from_field_name: lambda _, v: GreaterThanOrEqual(
            F(db_field_name), date_utils.str_to_search_datetime(v)),
        to_field_name: lambda _, v: LessThanOrEqual(
            F(db_field_name), date_utils.str_to_search_datetime(v)),
    }
