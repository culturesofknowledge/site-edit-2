from django import forms
from django.forms import ModelForm

from core.form_label_maps import field_label_map
from core.helper import form_utils
from core.helper.form_utils import SearchCharField, SearchIntField
from publication.models import CofkUnionPublication

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

    publication_details = SearchCharField()
    publication_details_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    abbrev = SearchCharField(label=field_label_map['publication']['abbrev'])
    abbrev_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    publication_id = SearchIntField()
    publication_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
