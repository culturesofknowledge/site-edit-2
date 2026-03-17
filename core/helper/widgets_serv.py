import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets

from core.helper.data_serv import check_test_general_true


def create_common_checkbox(**attrs):
    _attrs = {'class': 'elcheckbox'} | (attrs or {})
    return forms.CheckboxInput(_attrs, check_test=check_test_general_true)


class NewDateInput(widgets.Input):
    input_type = "text"

    def __init__(self, attrs=None):
        default_attrs = {
            'placeholder': 'DD/MM/YYYY',
            'style': 'width: 10em',
            'pattern': r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{4}|\d{4})',
            'title': 'Enter a date as DD/MM/YYYY, MM/YYYY, or YYYY',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class FlexibleDateField(forms.Field):
    """A form field that accepts dates in DD/MM/YYYY, MM/YYYY, or YYYY format.
    Stores as a date object (padding missing day/month with 1).
    Displays existing dates as DD/MM/YYYY.
    """
    widget = NewDateInput

    def prepare_value(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%d/%m/%Y')
        return value

    def clean(self, value):
        value = super().clean(value)
        if not value:
            return None
        value = value.strip()
        if not value:
            return None

        # Try DD/MM/YYYY
        m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', value)
        if m:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                return datetime.date(year, month, day)
            except ValueError:
                raise ValidationError('Enter a valid date in DD/MM/YYYY or MM/YYYY or YYYY format.')

        # Try MM/YYYY
        m = re.fullmatch(r'(\d{1,2})/(\d{4})', value)
        if m:
            month, year = int(m.group(1)), int(m.group(2))
            if month < 1 or month > 12:
                raise ValidationError('Month must be between 1 and 12.')
            try:
                return datetime.date(year, month, 1)
            except ValueError:
                raise ValidationError('Enter a valid date in MM/YYYY format.')

        # Try YYYY
        m = re.fullmatch(r'(\d{4})', value)
        if m:
            year = int(m.group(1))
            try:
                return datetime.date(year, 1, 1)
            except ValueError:
                raise ValidationError('Enter a valid year in YYYY format.')

        raise ValidationError('Enter a date in DD/MM/YYYY, MM/YYYY, or YYYY format.')


class SearchDateTimeInput(widgets.Input):
    input_type = "text"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {'class': 'dateinput'}
        elif 'class' in attrs:
            attrs['class'] += ' dateinput'
        super().__init__(attrs)


class Datalist(widgets.ChoiceWidget):
    template_name = 'core/widget/datalist.html'
    option_template_name = "django/forms/widgets/select_option.html"

    def __init__(self, attrs=None, choices=()):
        # attrs = {'id': datalist_id} or attrs or {}
        super().__init__(attrs)
        self.choices = list(choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["choices"] = self.choices
        return context


class EmloCheckboxSelectMultiple(widgets.CheckboxSelectMultiple):
    option_template_name = 'core/widget/emlo_checkbox.html'
