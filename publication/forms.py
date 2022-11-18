from django import forms
from django.forms import ModelForm, CharField, IntegerField

from core.helper import form_utils, widgets_utils
from publication.models import CofkUnionPublication


class PublicationForm(ModelForm):
    publication_details = forms.CharField(required=True, widget=forms.Textarea())
    abbrev = forms.CharField(required=False, max_length=50)

    class Meta:
        model = CofkUnionPublication
        fields = (
            'publication_details',
            'abbrev',
        )


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'publication/component/publication_search_fieldset.html'

    publication_details = CharField(required=False)
    publication_details_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    abbrev = forms.CharField(required=False, label='Abbreviation' )
    abbrev_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_user = forms.CharField(required=False, label='Last changed by')
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_timestamp_from = forms.DateField(required=False, widget=widgets_utils.NewDateInput())
    change_timestamp_to = forms.DateField(required=False, widget=widgets_utils.NewDateInput())

    publication_id = IntegerField(required=False, label='Location id')
    publication_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
