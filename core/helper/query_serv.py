import functools
import logging
from typing import Callable, Iterable

from django.db.models import F, Exists, OuterRef
from django.db.models import Q, Lookup, lookups
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual

from core.helper import date_serv

log = logging.getLogger(__name__)

person_detail_fields = [
    'date_of_birth_year',
    'date_of_death_year',
    'date_of_death_is_range',
    'date_of_birth_is_range',
    'foaf_name',
    'skos_altlabel',
    'person_aliases',
]
comment_detail_fields = [
    'comment',
]
location_detail_fields = [
    'location_name',
]
image_detail_fields = [
    'image_filename',
]
resource_detail_fields = [
    'resource_name',
    'resource_details',
    'resource_url',
]


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
                                   search_field_names: list[str],
                                   search_fields_maps: dict[str, Iterable[str]] = None,
                                   search_fields_fn_maps: dict[str, Callable] = None,
                                   ) -> Iterable[Q]:
    """
    :param search_fields_maps
    used to define one or more aliases for lookup search field
    e.g. {'date_of_birth_year': ['mydate1', 'mydate2']}
    it will look up db field `mydate1` and `mydate2` instead of `date_of_birth_year`
    """
    for field_name in search_field_names:
        field_val = request_data.get(field_name)
        lookup_key = request_data.get(f'{field_name}_lookup')

        if not field_val and lookup_key not in nullable_lookup_keys:
            continue

        if (lookup_fn := choices_lookup_map.get(lookup_key)) is None:
            log.warning(f'lookup fn not found -- [{field_name}][{lookup_key}]')
            continue

        if search_fields_maps and field_name in search_fields_maps:
            # handle search_fields_maps

            _names = list(search_fields_maps[field_name])
            if (lookup_idx := lookup_idx_map.get(lookup_key)) is not None:
                _names = [_names[lookup_idx]]
            conn_type = lookup_conn_type_map.get(lookup_key, Q.OR)

            q = Q()
            for search_field in _names:
                log.debug(f'query cond: field_name[{field_name}] search_field[{search_field}] '
                          f'field_val[{field_val}] lookup_key[{lookup_key}]')
                q.add(run_lookup_fn(lookup_fn, search_field, field_val), conn_type)

            yield q

        elif search_fields_fn_maps and field_name in search_fields_fn_maps:
            # handle search_fields_fn_maps
            log.debug(f'query cond: field_name[{field_name}] field_val[{field_val}] lookup_key[{lookup_key}]')
            yield search_fields_fn_maps[field_name](lookup_fn, field_name, field_val)

        else:
            # handle normal case
            log.debug(f'query cond: field_name[{field_name}] field_val[{field_val}] lookup_key[{lookup_key}]')
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
    None: lookups.IExact,
    '': lookups.IExact,
}

""" 
if value of search_fields_maps have more than one element,
some lookup key may only apply in first or last element,

0 == first element
-1 == last element
None == all element
"""
lookup_idx_map = {
    'starts_with': 0,
    'not_start_with': 0,
    'ends_with': -1,
    'not_end_with': -1,
}


"""
default lookup connection type is `Q.OR`
"""
lookup_conn_type_map = {
    'is_blank': Q.AND,
    'not_contain': Q.AND,
}

nullable_lookup_keys = [
    'is_blank', 'not_blank',
]


def create_from_to_datetime(from_field_name: str, to_field_name: str,
                            db_field_name: str, convert_fn: Callable = None) -> dict:
    if convert_fn is None:
        convert_fn = date_serv.str_to_search_datetime

    return {
        from_field_name: lambda _, v: GreaterThanOrEqual(
            F(db_field_name), convert_fn(v)),
        to_field_name: lambda _, v: LessThanOrEqual(
            F(db_field_name), convert_fn(v)),
    }


def create_exists_by_mode(model_class, queries, annotate: dict = None) -> Exists:
    queryset = model_class.objects
    if annotate:
        queryset = queryset.annotate(**annotate)

    return Exists(
        queryset.filter(
            all_queries_match(queries),
            pk=OuterRef('pk'),
        )
    )


def update_queryset(queryset,
                    model_class, queries=None,
                    annotate: dict = None,
                    sort_by=None, ):
    """
    help you to update queryset

    it's new method compare to view_serv.create_queryset_by_queries
    """

    if annotate:
        queryset = queryset.annotate(**annotate)

    if queries:
        queryset = queryset.filter(
            create_exists_by_mode(model_class, queries, annotate=annotate)
        )

    if sort_by:
        queryset = queryset.order_by(*sort_by)

    log.debug(f'queryset sql\n: {str(queryset.query)}')
    return queryset


def create_recref_lookup_fn(rel_types: list, recref_field_name: str, cond_fields: list[str]):
    recref_name = '__'.join(recref_field_name.split('__')[:-1])

    def _fn(lookup_fn, f, v):
        query = Q(**{
            f'{recref_name}__relationship_type__in': rel_types,
        })
        cond_query = create_q_by_field_names(
            lookup_fn,
            join_fields(recref_field_name, cond_fields),
            v
        )
        return query & cond_query

    return _fn


def create_q_by_field_names(lookup_fn: Callable, field_names: Iterable[str], field_val: str,
                            conn_type=Q.OR) -> Q:
    q = Q()
    for n in field_names:
        q.add(run_lookup_fn(lookup_fn, n, field_val), conn_type)
    return q


def join_fields(parent_field: str, child_fields: Iterable[str]) -> Iterable[str]:
    return (
        f'{parent_field}__{n}' for n in child_fields
    )
