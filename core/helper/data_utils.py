import collections
from typing import Iterable, Callable


def group_by(records: Iterable, key_fn: Callable) -> dict:
    records_dict = collections.defaultdict(list)
    for r in records:
        records_dict[key_fn(r)].append(r)
    return records_dict
