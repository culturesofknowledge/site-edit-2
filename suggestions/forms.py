from django import forms
from .models import CofkSuggestions
from core.helper import form_serv

class SuggestionForm(forms.Form):
    suggestion_text = forms.CharField(max_length = 4096, widget=forms.Textarea(attrs={'rows':30}))

    class Meta:
        model = CofkSuggestions
        fields = ['suggestion_text']

class SuggestionFilterForm(forms.Form):
    # person       = forms.BooleanField(required=True, initial=True)
    # location     = forms.BooleanField(required=True, initial=True)
    # publication  = forms.BooleanField(required=True, initial=True)
    # institution  = forms.BooleanField(required=True, initial=True)
    # showNew      = forms.BooleanField(required=True, initial=True, label="Show New")
    # showExisting = forms.BooleanField(required=True, initial=True, label="Show Existing")
    person       = form_serv.ZeroOneCheckboxField(is_str=False, initial=1)
    location     = form_serv.ZeroOneCheckboxField(is_str=False, initial=1)
    publication  = form_serv.ZeroOneCheckboxField(is_str=False, initial=1)
    institution  = form_serv.ZeroOneCheckboxField(is_str=False, initial=1)
    showNew      = form_serv.ZeroOneCheckboxField(is_str=False, initial=1, label="Show New")
    showExisting = form_serv.ZeroOneCheckboxField(is_str=False, initial=1, label="Show Existing")

    class Meta:
        model = CofkSuggestions
        fields = '__all__'
