import collections
from typing import Iterable, Callable


def group_by(records: Iterable, key_fn: Callable, val_fn: Callable = None) -> dict:
    val_fn = val_fn or (lambda x: x)
    records_dict = collections.defaultdict(list)
    for r in records:
        records_dict[key_fn(r)].append(val_fn(r))
    return records_dict


def to_str_list_no_none(values: Iterable) -> Iterable[str]:
    return (str(v) if v is not None else '' for v in values)
