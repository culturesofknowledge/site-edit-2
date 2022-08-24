from django import forms


def one_zero_check_test(value):
    return value == '1' or value is True


def create_common_checkbox(**attrs):
    _attrs = {'class': 'elcheckbox'} | (attrs or {})
    return forms.CheckboxInput(_attrs, check_test=one_zero_check_test)
