import functools
from typing import Iterable, Callable

from django.contrib.postgres.aggregates import StringAgg
from django.core.cache import cache
from django.db.models import TextField, Value, Q, Lookup, F, lookups, Exists, OuterRef
from django.db.models.functions import Concat, Cast

default_output_field = TextField()


def concat_safe(items: Iterable, output_field=default_output_field):
    return Concat(
        *[Cast(f, output_field) for f in items]
    )


def join_values_for_search(fields, output_field=default_output_field):
    """
    use this function in annotate, it will 'group by' and 'concat all' fields, values and return a string
    the returned string can be used in search and sorting
    """

    if isinstance(fields, list or Iterable):
        fields = concat_safe(fields)

    return StringAgg(fields, '', default=Value(''), output_field=output_field)


def join_fields(parent_field: str, child_fields: Iterable[str]) -> Iterable[str]:
    return (
        f'{parent_field}__{n}' for n in child_fields
    )


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


def create_q_by_field_names(lookup_fn: Callable, field_names: Iterable[str], field_val: str,
                            conn_type=Q.OR) -> Q:
    q = Q()
    for n in field_names:
        q.add(run_lookup_fn(lookup_fn, n, field_val), conn_type)
    return q


def cond_not(lookup_fn: Callable) -> Callable:
    """
    add not condition to lookup_fn
    """

    def _fn(field, val):
        q = lookup_fn(F(field), val)
        if not isinstance(q, Q):
            q = Q(q)
        return ~q

    return _fn


def is_null(field, val) -> Callable:
    if not isinstance(field, F):
        field = F(field)
    return lookups.IsNull(field, True)


def is_blank(field, val) -> Callable:
    if not isinstance(field, F):
        field = F(field)
    field = Cast(field, TextField())
    return lookups.IsNull(field, True) | lookups.Exact(field, '')


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


def load_cache(key, data_fn, expires=10800):
    result = cache.get(key)
    if result is None:
        result = data_fn()
        cache.set(key, result, expires)
    return result
