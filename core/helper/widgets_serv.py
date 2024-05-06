from django import forms
from django.forms import widgets

from core.helper.data_serv import check_test_general_true


def create_common_checkbox(**attrs):
    _attrs = {'class': 'elcheckbox'} | (attrs or {})
    return forms.CheckboxInput(_attrs, check_test=check_test_general_true)


class NewDateInput(widgets.Input):
    input_type = "date"


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
