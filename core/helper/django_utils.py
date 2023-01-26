import itertools
from typing import Iterable

from django.apps import apps


def all_model_classes() -> Iterable:
    return itertools.chain.from_iterable(
        i.values() for i in apps.all_models.values()
    )
