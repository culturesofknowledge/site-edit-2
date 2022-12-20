from django import forms
from django.forms import ModelForm

from core.helper import form_utils
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
            'change_user'
        )


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'institution/component/institution_search_fieldset.html'

    institution_name = forms.CharField(required=False, label='Name')
    institution_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_city = forms.CharField(required=False, label='City')
    institution_city_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_country = forms.CharField(required=False, label='Country')
    institution_country_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    resources = forms.CharField(required=False, label='Related resources', help_text='E.g. links to online catalogues.')
    resources_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    editors_notes = forms.CharField(required=False, label="Editors' notes")
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    images = forms.CharField(required=False)
    images_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_timestamp_from = forms.CharField(required=False)
    change_timestamp_to = forms.CharField(required=False)
    change_timestamp_info = form_utils.datetime_search_info

    change_user = forms.CharField(required=False, help_text='Username of the person who last changed the record.')
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_id = forms.IntegerField(required=False, min_value=1, label='Repository id',
                                        help_text='The unique ID for the record within this database.')
    institution_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
