import itertools


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
