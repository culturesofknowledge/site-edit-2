import logging
from typing import Iterable

from django.template.loader import render_to_string

log = logging.getLogger(__name__)


def record_tracker_label_fn_factory(subject='Entry'):
    def _fn(_self):
        context = {k: _self[k].value() for k in
                   ['creation_timestamp', 'creation_user', 'change_timestamp', 'change_user', ]}

        context = context | {'subject': subject}
        return render_to_string('core/component/record_tracker_label.html', context)

    return _fn


def _filter_and_log_field_names(cleaned_data: dict, field_names: Iterable[str]):
    def _filter_with_log_fn(_field_name):
        if _field_name not in cleaned_data:
            msg = f'field[{_field_name}] not found in cleaned_data'
            log.warning(msg)
            return False
        else:
            return True

    return filter(_filter_with_log_fn, field_names)


def _prepare_valid_field_names(cleaned_data, field_names):
    field_names = [field_names] if isinstance(field_names, str) else field_names
    field_names = _filter_and_log_field_names(cleaned_data, field_names)
    return field_names


def clean_checkbox_to_one_zero(cleaned_data: dict, field_names: Iterable[str] | str):
    """ DB required store value as '1' and '0'
    we can use this method change form value from True or False to '1' and '0'
    """

    for f in _prepare_valid_field_names(cleaned_data, field_names):
        cleaned_data[f] = '1' if cleaned_data[f] else '0'


def clean_by_default_value(cleaned_data: dict, field_names: Iterable[str],
                           default_val, is_empty_fn=None, ):
    is_empty_fn = is_empty_fn or (lambda v: v is None)

    # default value
    for field in _prepare_valid_field_names(cleaned_data, field_names):
        if is_empty_fn(cleaned_data[field]):
            cleaned_data[field] = default_val
