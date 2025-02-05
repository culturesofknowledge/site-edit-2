from django import forms
from .models import CofkSuggestions
from core.helper import form_serv

# Form to getting suggestion text
class SuggestionForm(forms.Form):
    suggestion_text = forms.CharField(max_length = 4096, widget=forms.Textarea(attrs={'rows':30}))

    class Meta:
        model = CofkSuggestions
        fields = ['suggestion_text']

# Form for filtering displayed suggestions of the given user
class SuggestionFilterForm(forms.Form):
    person       = forms.BooleanField(required=True, initial=True, label="Person")
    location     = forms.BooleanField(required=True, initial=True, label="Location")
    publication  = forms.BooleanField(required=True, initial=True, label="Institution")
    institution  = forms.BooleanField(required=True, initial=True, label="Publication")
    showNew      = forms.BooleanField(required=True, initial=True, label="Show New")
    showExisting = forms.BooleanField(required=True, initial=True, label="Show Existing")

    class Meta:
        fields = [ 'person', 'location', 'publication', 'institution',
                  'showNew', 'showExisting']
    