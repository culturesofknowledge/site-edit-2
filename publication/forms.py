from django import forms
from django.forms import ModelForm

from core.form_label_maps import field_label_map
from core.helper import form_serv
from core.helper.form_serv import SearchCharField, SearchIntField
from publication.models import CofkUnionPublication


class PublicationForm(ModelForm):
    publication_details = form_serv.CommonTextareaField(
        required=True,
        help_text="e.g.: AuthorSurname, Forename, ‘Title of publication’ (Place of publication: publisher if known, YYYY) "
                  "<br/>or: AuthorSurname, Forename, ‘Title of article’, ‘Title of Journal’, issue no (YYYY)"
    )
    abbrev = forms.CharField(
        required=False,
        max_length=50,
        help_text='Optional short form of the full publication details.'
    )

    class Meta:
        model = CofkUnionPublication
        fields = (
            'publication_details',
            'abbrev',
        )


class GeneralSearchFieldset(form_serv.BasicSearchFieldset):
    title = 'General'
    template_name = 'publication/component/publication_search_fieldset.html'

    publication_details = SearchCharField(
        help_text='E.g. author(s)/editor(s), title, place and year of publication.'
    )
    publication_details_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    abbrev = SearchCharField(
        label=field_label_map['publication']['abbrev'],
        help_text='Optional short form of the full publication details.'
    )
    abbrev_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    publication_id = SearchIntField(
        label=field_label_map['publication']['publication_id'],
        help_text='The unique ID for the record within this database.'
    )
    publication_id_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)
