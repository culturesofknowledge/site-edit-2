from django import forms
from django.forms import widgets


def check_test_general_true(value):
    return value == '1' or value == 1 or value is True


def create_common_checkbox(**attrs):
    _attrs = {'class': 'elcheckbox'} | (attrs or {})
    return forms.CheckboxInput(_attrs, check_test=check_test_general_true)


class NewDateInput(widgets.Input):
    input_type = "text"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {'class': 'dateinput'}
        else:
            attrs['class'] = 'dateinput'
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

