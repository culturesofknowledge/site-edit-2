import logging
from typing import Callable

from django.db import models
from django.db.models.base import ModelBase

from work.models import CofkUnionWork, CofkUnionQueryableWork

from work.work_utils import clone_queryable_work

log = logging.getLogger(__name__)


def on_clone_queryable_work(sender: ModelBase, instance: models.Model, created: bool,
                            raw: bool, using, update_fields, **kwargs):
    handle_work_signal(sender, instance, clone_queryable_work, **kwargs)


def on_delete_queryable_work(sender: ModelBase, instance: models.Model, using, **kwargs):
    def _del(work):
        CofkUnionQueryableWork.objects.filter(iwork_id=work.iwork_id).delete()

    handle_work_signal(sender, instance, _del, **kwargs)


def handle_work_signal(sender: ModelBase, instance: models.Model, handle_fn: Callable,
                       **kwargs):
    if sender != CofkUnionWork:
        return

    instance: CofkUnionWork
    try:
        handle_fn(instance)
    except Exception as e:
        log.error(f'failed to handle work signal [{instance.iwork_id}]')
        log.exception(e)
