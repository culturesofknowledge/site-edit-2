from django import forms
from django.forms import ModelForm

from core.helper import form_utils
from core.helper.form_utils import SearchCharField, SearchIntField
from institution.models import CofkUnionInstitution


class InstitutionForm(ModelForm):
    institution_name = forms.CharField()
    institution_city = forms.CharField()
    institution_country = forms.CharField()
    institution_synonyms = form_utils.CommonTextareaField()
    editors_notes = form_utils.CommonTextareaField()
    institution_city_synonyms = form_utils.CommonTextareaField()
    institution_country_synonyms = form_utils.CommonTextareaField()

    class Meta:
        model = CofkUnionInstitution
        exclude = (
            'creation_user',
            'change_user',
            'resources',
            'images'
        )


field_label_map = { 'institution_name': 'Name',
                    'institution_city': 'City',
                    'institution_country': 'Country',
                    'resources': 'Related resources',
                    'editors_notes': "Editors' notes",
                    'institution_id': 'Repository id',
                    'images': 'Images',
                    'change_user': 'Last edited by'}

class GeneralSearchFieldset(form_utils.BasicSearchFieldset):
    title = 'General'
    template_name = 'institution/component/institution_search_fieldset.html'

    institution_name = SearchCharField(label=field_label_map['institution_name'],
                                       help_text='This field contains the primary name and'
                                                 ' any alternative names for a repository.')
    institution_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_city = SearchCharField(label='City',
                                       help_text='This field contains the primary city name and'
                                                 ' any alternative city names for a repository.')
    institution_city_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_country = SearchCharField(label='Country',
                                          help_text='This field contains the primary country name and'
                                                    ' any alternative country names for a repository.')
    institution_country_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    resources = SearchCharField(label='Related resources', help_text='E.g. links to online catalogues.')
    resources_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    editors_notes = SearchCharField(label="Editors' notes")
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    images = SearchCharField()
    images_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_id = SearchIntField(min_value=1, label='Repository id',
                                    help_text='The unique ID for the record within this database.')
    institution_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
