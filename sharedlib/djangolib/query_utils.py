from typing import Iterable

from django.contrib.postgres.aggregates import StringAgg
from django.db.models import TextField, Value
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
