import logging
from typing import Iterable

from django import forms
from django.template.loader import render_to_string

from core.helper import widgets_utils

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


def clean_by_default_value(cleaned_data: dict, field_names: Iterable[str],
                           default_val, is_empty_fn=None, ):
    is_empty_fn = is_empty_fn or (lambda v: v is None)

    # default value
    for field in _prepare_valid_field_names(cleaned_data, field_names):
        if is_empty_fn(cleaned_data[field]):
            cleaned_data[field] = default_val


class ZeroOneCheckboxField(forms.BooleanField):
    def __init__(self, is_str=True, *args, **kwargs):
        default_kwargs = dict(
            widget=widgets_utils.create_common_checkbox(),
            initial='0',
            required=False,
        )
        kwargs = default_kwargs | kwargs
        super().__init__(*args, **kwargs)

        self.is_str = is_str

    def clean(self, value):
        new_value = super().clean(value)
        if self.is_str:
            new_value = '1' if new_value else '0'
        else:
            new_value = 1 if new_value else 0
        return new_value
