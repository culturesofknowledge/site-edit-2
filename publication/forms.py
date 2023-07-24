from django import forms
from django.forms import ModelForm

from core.form_label_maps import field_label_map
from core.helper import form_serv
from core.helper.form_serv import SearchCharField, SearchIntField
from publication.models import CofkUnionPublication


class PublicationForm(ModelForm):
    publication_details = form_serv.CommonTextareaField(required=True)
    abbrev = forms.CharField(required=False, max_length=50)

    class Meta:
        model = CofkUnionPublication
        fields = (
            'publication_details',
            'abbrev',
        )


class GeneralSearchFieldset(form_serv.BasicSearchFieldset):
    title = 'General'
    template_name = 'publication/component/publication_search_fieldset.html'

    publication_details = SearchCharField()
    publication_details_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    abbrev = SearchCharField(label=field_label_map['publication']['abbrev'])
    abbrev_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    publication_id = SearchIntField()
    publication_id_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)
