from django import forms
from django.forms import ModelForm, CharField, IntegerField

from core.helper import form_utils
from publication.models import CofkUnionPublication

field_label_map = { 'publication_details': 'Publication details',
                    'abbrev': 'Abbreviation',
                    'change_user': 'Last edited by',
                    'publication_id': 'Publication id'}

class PublicationForm(ModelForm):
    publication_details = form_utils.CommonTextareaField(required=True)
    abbrev = forms.CharField(required=False, max_length=50)

    class Meta:
        model = CofkUnionPublication
        fields = (
            'publication_details',
            'abbrev',
        )


class GeneralSearchFieldset(form_utils.BasicSearchFieldset):
    title = 'General'
    template_name = 'publication/component/publication_search_fieldset.html'

    publication_details = CharField(required=False)
    publication_details_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    abbrev = forms.CharField(required=False, label='Abbreviation')
    abbrev_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    publication_id = IntegerField(required=False)
    publication_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
