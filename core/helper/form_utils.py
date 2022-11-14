import logging
import warnings
from typing import Iterable

from django import forms
from django.db.models import TextChoices
from django.forms import BoundField
from django.template.loader import render_to_string

from core.helper import widgets_utils

log = logging.getLogger(__name__)

short_month_choices = [
    (None, ''),
    (1, 'Jan'),
    (2, 'Feb'),
    (3, 'Mar'),
    (4, 'Apr'),
    (5, 'May'),
    (6, 'Jun'),
    (7, 'Jul'),
    (8, 'Aug'),
    (9, 'Sep'),
    (10, 'Oct'),
    (11, 'Nov'),
    (12, 'Dec'),
]


def record_tracker_label_fn_factory(subject='Entry'):
    def _fn(_self):
        context = {k: _self[k].value() for k in
                   ['creation_timestamp', 'creation_user', 'change_timestamp', 'change_user', ]}

        context = context | {'subject': subject}
        return render_to_string('core/component/record_tracker_label.html', context)

    return _fn


def filter_and_log_field_names(cleaned_data: dict, field_names: Iterable[str]):
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
    field_names = filter_and_log_field_names(cleaned_data, field_names)
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


class ThreeFieldDateField(forms.Field):
    """
    remember update form (get_initial_for_field, clean) to trigger
    get_initial_by_initial_dict, clean_other_fields
    TOBEREMOVE no longer need
    """
    warnings.warn('ThreeFieldDateField logic no longer used, to be remove', DeprecationWarning)

    def __init__(self, year_field_name,
                 month_field_name,
                 day_field_name,
                 *args, **kwargs):
        default_kwargs = dict(
            widget=widgets_utils.NewDateInput(),
            # initial='0',
            required=False,
        )
        kwargs = default_kwargs | kwargs
        super().__init__(*args, **kwargs)

        self.year_field_name = year_field_name
        self.month_field_name = month_field_name
        self.day_field_name = day_field_name

    def get_initial_by_initial_dict(self, field_name: str, initial: dict):
        year = initial.get(self.year_field_name, None)
        month = initial.get(self.month_field_name, None)
        day = initial.get(self.day_field_name, None)
        if year and month and day:
            return f'{year}-{month:0>2}-{day:0>2}'
        return ''

    def clean_other_fields(self, cleaned_data: dict, value: str):
        date_values = value and value.split('-')
        if len(date_values) != 3:
            return

        (
            cleaned_data[self.year_field_name],
            cleaned_data[self.month_field_name],
            cleaned_data[self.day_field_name],
        ) = date_values

        return cleaned_data


class IntLookupChoices(TextChoices):
    EQUALS = 'equals', 'equals (=)',
    NOT_EQUAL_TO = 'not_equal_to', 'not equal to (!=)',

    LESS_THAN = 'less_than', 'less than (<)'
    GREATER_THAN = 'greater_than', 'greater than (>)'

    IS_BLANK = 'is_blank', 'is blank',
    NOT_BLANK = 'not_blank', 'not blank',


class StrLookupChoices(TextChoices):
    CONTAINS = 'contains', 'contains',
    DOES_NOT_CONTAIN = 'not_contain', 'not contain',

    STARTS_WITH = 'starts_with', 'starts with',
    DOES_NOT_START_WITH = 'not_start_with', 'not start with',
    ENDS_WITH = 'ends_with', 'ends with',
    DOES_NOT_END_WITH = 'not_end_with', 'not end with',

    EQUALS = 'equals', 'equals (=)',
    NOT_EQUAL_TO = 'not_equal_to', 'not equal to (!=)',

    IS_BLANK = 'is_blank', 'is blank',
    NOT_BLANK = 'not_blank', 'not blank',


class EqualSimpleLookupChoices(TextChoices):
    EQUALS = 'equals', 'equals (=)',
    NOT_EQUAL_TO = 'not_equal_to', 'not equal to (!=)',

    IS_BLANK = 'is_blank', 'is blank',
    NOT_BLANK = 'not_blank', 'not blank',


def create_day_field(required=False):
    return forms.IntegerField(required=required, min_value=1, max_value=31,
                              widget=forms.TextInput(
                                  attrs={
                                      'placeholder': 'DD',
                                      'type': 'number',
                                      'min': 1,
                                      'max': 31,
                                      'class': 'ad-day',
                                  }
                              ))


def create_month_field(required=False):
    return forms.IntegerField(required=required,
                              widget=forms.Select(choices=short_month_choices,
                                                  attrs={
                                                      'class': 'ad-month',
                                                  }
                                                  ))


def create_year_field(required=False):
    return forms.IntegerField(required=required, min_value=1, max_value=9999,
                              widget=forms.TextInput(
                                  attrs={
                                      'placeholder': 'YYYY',
                                      'type': 'number',
                                      'min': 1,
                                      'max': 9999,
                                      'class': 'ad-year',
                                  }
                              ))


def create_lookup_field(choices, required=False):
    return forms.CharField(required=required,
                           widget=forms.Select(choices=choices), )


class SelectedRecrefField(forms.CharField):
    def get_recref_name(self, target_id):
        raise NotImplementedError()

    def get_bound_field(self, form, field_name):
        target_id = form.initial.get(field_name)
        return RecrefSelectBound(form, self, field_name, self.get_recref_name(target_id))


class RecrefSelectBound(BoundField):

    def __init__(self, form, field, name, recref_name):
        super().__init__(form, field, name)
        self.recref_name = recref_name


class CharSelectField(forms.CharField):
    def __init__(self, choices, required=False, **kwargs):
        super().__init__(required=required,
                         widget=forms.Select(choices=choices),
                         initial=choices[0][0],  # this can avoid invalid changed_data
                         **kwargs)
