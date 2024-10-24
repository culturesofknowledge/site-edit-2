from django import forms
from django.forms import ModelForm

from core.form_label_maps import field_label_map
from core.helper import form_serv
from core.helper.form_serv import SearchCharField, SearchIntField
from institution.models import CofkUnionInstitution


class InstitutionForm(ModelForm):
    institution_name = forms.CharField()
    institution_city = forms.CharField()
    institution_country = forms.CharField()
    institution_synonyms = form_serv.CommonTextareaField()
    editors_notes = form_serv.CommonTextareaField()
    institution_city_synonyms = form_serv.CommonTextareaField()
    institution_country_synonyms = form_serv.CommonTextareaField()

    class Meta:
        model = CofkUnionInstitution
        exclude = (
            'creation_user',
            'change_user',
            'resources',
            'images'
        )


class GeneralSearchFieldset(form_serv.BasicSearchFieldset):
    title = 'General'
    template_name = 'institution/component/institution_search_fieldset.html'

    institution_name = SearchCharField(label=field_label_map['institution']['institution_name'],
                                       help_text='This field contains the primary name and'
                                                 ' any alternative names for a repository.')
    institution_name_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    institution_city = SearchCharField(label=field_label_map['institution']['institution_city'],
                                       help_text='This field contains the primary city name and'
                                                 ' any alternative city names for a repository.')
    institution_city_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    institution_country = SearchCharField(label=field_label_map['institution']['institution_country'],
                                          help_text='This field contains the primary country name and'
                                                    ' any alternative country names for a repository.')
    institution_country_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    resources = SearchCharField(label=field_label_map['institution']['resources'],
                                help_text='E.g. links to online catalogues.')
    resources_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    editors_notes = SearchCharField(label=field_label_map['institution']['editors_notes'])
    editors_notes_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    images = SearchCharField()
    images_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    institution_id = SearchIntField(min_value=1, label=field_label_map['institution']['institution_id'],
                                    help_text='The unique ID for the record within this database.')
    institution_id_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)
    tombstone = form_serv.TombstoneSelect()
