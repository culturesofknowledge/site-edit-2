import logging
from typing import Callable, Iterable, Any

from django.db.models import F, QuerySet
from django.db.models import Q, lookups
from django.db.models.base import ModelBase
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual

from cllib_django.query_utils import join_fields, run_lookup_fn, create_q_by_field_names, \
    cond_not, is_blank, create_exists_by_mode, is_null
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


def create_eq_query(field, value) -> Q:
    return Q(**{field: value})


def create_queries_by_field_fn_maps(field_fn_maps: dict, data: dict) -> list[Q]:
    query_field_values = ((f, data.get(f)) for f in field_fn_maps.keys())
    query_field_values = ((f, v) for f, v in query_field_values if v)
    queries = [run_lookup_fn(field_fn_maps[f], f, v)
               for f, v in query_field_values]
    return queries


def create_queries_by_lookup_field(request_data: dict,
                                   search_field_names: list[str],
                                   search_fields_maps: dict[str, Iterable[str]] = None,
                                   search_fields_fn_maps: dict[str, 'LookupFn'] = None,
                                   ) -> Iterable[Q]:
    """
    :param search_fields_maps
    used to define one or more aliases for lookup search field
    e.g. {'date_of_birth_year': ['mydate1', 'mydate2']}
    it will look up db field `mydate1` and `mydate2` instead of `date_of_birth_year`

    :param search_fields_fn_maps
    allow to define more complex lookup function, for example multi relationship query
    Lookupfn is Callable and return a Q object

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
            conn_type = get_lookup_conn_type_by_lookup_key(lookup_key)

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


def lookup_icontains_wildcard(field, value):
    field = F(field)
    if isinstance(value, str) and '%' in value:
        return lookups.IRegex(field, value.replace('%', '.*'))
    else:
        return lookups.IContains(field, value)


choices_lookup_map = {
    'contains': lookup_icontains_wildcard,
    'starts_with': lookups.IStartsWith,
    'ends_with': lookups.IEndsWith,
    'equals': lookups.IExact,
    'not_contain': cond_not(lookup_icontains_wildcard),
    'not_start_with': cond_not(lookups.IStartsWith),
    'not_end_with': cond_not(lookups.IEndsWith),
    'not_equal_to': cond_not(lookups.IExact),
    'is_blank': is_blank,
    'is_null': is_null,
    'not_blank': cond_not(is_blank),
    'not_null': cond_not(is_null),
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
    'is_null': Q.AND,
    'not_contain': Q.AND,
}

nullable_lookup_keys = [
    'is_blank', 'not_blank',
    'is_null', 'not_null',
]


def get_lookup_key_by_lookup_fn(lookup_fn):
    for k, v in choices_lookup_map.items():
        if v == lookup_fn:
            return k
    return None


def get_lookup_conn_type_by_lookup_key(lookup_key):
    return lookup_conn_type_map.get(lookup_key, Q.OR)


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


def update_queryset(queryset: QuerySet,
                    model_class: ModelBase,
                    queries: Iterable[Q] = None,
                    annotate: dict = None,
                    sort_by: Iterable[str] = None, ):
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

    log.debug('queryset sql\n: %s', convert_queryset_to_sql(queryset))
    return queryset


LookupFn = Callable[[Callable, str, Any], Q]


def create_recref_lookup_fn(rel_types: list, recref_field_name: str, cond_fields: list[str]) -> LookupFn:
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


def convert_queryset_to_sql(queryset: QuerySet) -> str:
    return str(queryset.query)
