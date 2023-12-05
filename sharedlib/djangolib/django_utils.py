import functools
import itertools
import logging
from typing import Iterable

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest

from cllib.debug_utils import Timer

log = logging.getLogger(__name__)


def all_model_classes() -> Iterable:
    return itertools.chain.from_iterable(
        i.values() for i in apps.all_models.values()
    )


def log_request_time(func):
    # @debug_utils.Timer(log_fn=log.info).measure_fn
    @functools.wraps(func)
    def _fn(*args, **kwargs):
        req = next((a for a in args if isinstance(a, WSGIRequest)), None)
        name = None
        if req is not None:
            name = req.path

        with Timer(name=name, log_fn=log.info):
            result = func(*args, **kwargs)
        return result

    return _fn
