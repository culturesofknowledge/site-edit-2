import itertools
from typing import Iterable, Any, Callable


class RecordCounter:
    def __init__(self):
        self.counter = itertools.count()
        self._cur_size = -1

    def __call__(self, item):
        self.plus_one()
        return item

    def plus_one(self):
        self._cur_size = next(self.counter)

    def cur_size(self):
        return self._cur_size + 1


def split(values: Iterable, cond_fn: Callable[[Any], bool]):
    a, b = itertools.tee(values)
    return (i for i in a if cond_fn(i)), (i for i in b if not cond_fn(i))
