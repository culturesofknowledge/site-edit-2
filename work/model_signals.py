import logging
from typing import Callable

from django.db import models
from django.db.models.base import ModelBase

from core import constant
from core.helper import model_utils
from uploader.models import CofkLookupCatalogue

from work.models import CofkUnionWork, CofkUnionQueryableWork
import datetime

log = logging.getLogger(__name__)


def get_original_catalogue_val(work: CofkUnionWork, field_name):
    if work.original_catalogue_id:
        return work.original_catalogue.catalogue_code
    else:
        return CofkLookupCatalogue.objects.filter(catalogue_code='').first().catalogue_code or ''


special_clone_fields = {
    'original_catalogue': get_original_catalogue_val,
    'date_of_work_std': lambda w, n: datetime.datetime.strptime(
        w.date_of_work_std or constant.DEFAULT_EMPTY_DATE_STR,
        constant.STD_DATE_FORMAT).date(),
}


def get_clone_value_default(work: CofkUnionWork, field_name):
    return getattr(work, field_name)


def get_clone_value(work: CofkUnionWork, field_name):
    val_fn = special_clone_fields.get(field_name, get_clone_value_default)
    return val_fn(work, field_name)


def clone_queryable_work(work: CofkUnionWork):
    exclude_fields = {'iwork_id'}
    queryable_work = model_utils.get_safe(
        CofkUnionQueryableWork, iwork_id=work.iwork_id
    ) or CofkUnionQueryableWork()

    queryable_field_names = {field for field in dir(CofkUnionQueryableWork) if field not in exclude_fields}
    work_field_names = (field.name for field in work._meta.get_fields()
                        if hasattr(field, 'column'))
    common_field_names = (name for name in work_field_names
                          if name in queryable_field_names)
    field_val_list = ((name, get_clone_value(work, name)) for name in common_field_names)
    updated_field_val_list = ((name, val) for name, val in field_val_list
                              if getattr(queryable_work, name) != val)
    updated_field_dict = dict(updated_field_val_list)
    if not updated_field_dict:
        log.debug(f'skip save queryable work, no update_fields found [{work.iwork_id=}]')
        return

    for name, val in updated_field_dict.items():
        setattr(queryable_work, name, val)

    queryable_work.iwork_id = work.iwork_id
    queryable_work.creators_for_display = work.creators_for_display
    queryable_work.places_from_for_display = work.places_from_for_display
    queryable_work.places_to_for_display = work.places_to_for_display
    queryable_work.addressees_for_display = work.addressees_for_display

    queryable_work.save()
    log.info(f'queryable_work saved. [{work.iwork_id}][{list(updated_field_dict.keys())}]  ')


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
