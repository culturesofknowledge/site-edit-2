import calendar
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
            'pattern': r'(\d{1,2}/\d{1,2}/\d+|\d{1,2}/\d+|\d+)',
            'title': 'Enter a date as DD/MM/YYYY, MM/YYYY, or YYYY',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class FlexibleDateField(forms.Field):
    """A form field that accepts dates in DD/MM/YYYY, MM/YYYY, or YYYY format.
    Stores as a date object. Displays existing dates as DD/MM/YYYY.
    Subclasses FromDateField and ToDateField control how partial dates are defaulted.
    """
    widget = NewDateInput

    def prepare_value(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%d/%m/%Y')
        return value

    def _validate_and_parse(self, value):
        """Parse and validate the date string. Returns (year, month, day, format_type).
        format_type is 'full', 'month_year', or 'year'.
        """
        # Try DD/MM/YYYY
        m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d+)', value)
        if m:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if len(m.group(3)) != 4:
                raise ValidationError('Year must contain four digits.')
            if month < 1 or month > 12:
                raise ValidationError('Month must be between 1 and 12.')
            if day < 1 or day > 31:
                raise ValidationError('Day must be between 1 and 31.')
            max_day = calendar.monthrange(year, month)[1]
            if day > max_day:
                month_name = calendar.month_name[month]
                raise ValidationError(f'{month_name} {year} only has {max_day} days.')
            return year, month, day, 'full'

        # Try MM/YYYY
        m = re.fullmatch(r'(\d{1,2})/(\d+)', value)
        if m:
            month, year = int(m.group(1)), int(m.group(2))
            if len(m.group(2)) != 4:
                raise ValidationError('Year must contain four digits.')
            if month < 1 or month > 12:
                raise ValidationError('Month must be between 1 and 12.')
            return year, month, None, 'month_year'

        # Try YYYY (exactly 4 digits)
        m = re.fullmatch(r'(\d+)', value)
        if m:
            if len(m.group(1)) != 4:
                raise ValidationError('Year must contain four digits.')
            year = int(m.group(1))
            return year, None, None, 'year'

        raise ValidationError('Enter a date in DD/MM/YYYY, MM/YYYY, or YYYY format.')

    def _default_date(self, year, month, day, format_type):
        """Default partial dates. Base implementation defaults to start of period."""
        if format_type == 'full':
            return datetime.date(year, month, day)
        elif format_type == 'month_year':
            return datetime.date(year, month, 1)
        else:
            return datetime.date(year, 1, 1)

    def clean(self, value):
        value = super().clean(value)
        if not value:
            return None
        value = value.strip()
        if not value:
            return None

        year, month, day, format_type = self._validate_and_parse(value)
        try:
            return self._default_date(year, month, day, format_type)
        except ValueError:
            raise ValidationError('Enter a valid date in DD/MM/YYYY, MM/YYYY, or YYYY format.')


class FromDateField(FlexibleDateField):
    """Date field for 'From' dates. Partial dates default to start of period.
    YYYY -> 01/01/YYYY, MM/YYYY -> 01/MM/YYYY
    """

    def _default_date(self, year, month, day, format_type):
        if format_type == 'full':
            return datetime.date(year, month, day)
        elif format_type == 'month_year':
            return datetime.date(year, month, 1)
        else:
            return datetime.date(year, 1, 1)


class ToDateField(FlexibleDateField):
    """Date field for 'To' dates. Partial dates default to end of period.
    YYYY -> 31/12/YYYY, MM/YYYY -> last day of that month
    """

    def _default_date(self, year, month, day, format_type):
        if format_type == 'full':
            return datetime.date(year, month, day)
        elif format_type == 'month_year':
            last_day = calendar.monthrange(year, month)[1]
            return datetime.date(year, month, last_day)
        else:
            return datetime.date(year, 12, 31)


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
