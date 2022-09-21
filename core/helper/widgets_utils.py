from django import forms
from django.forms import widgets


def check_test_general_true(value):
    return value == '1' or value == 1 or value is True


def create_common_checkbox(**attrs):
    _attrs = {'class': 'elcheckbox'} | (attrs or {})
    return forms.CheckboxInput(_attrs, check_test=check_test_general_true)


class NewDateInput(widgets.Input):
    input_type = "date"
