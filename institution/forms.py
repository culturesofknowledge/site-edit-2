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

    institution_name = forms.CharField(required=False, )
    institution_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_synonyms = forms.CharField(required=False, )
    institution_synonyms_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_city = forms.CharField(required=False, )
    institution_city_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_city_synonyms = forms.CharField(required=False, )
    institution_city_synonyms_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_country = forms.CharField(required=False, )
    institution_country_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_country_synonyms = forms.CharField(required=False, )
    institution_country_synonyms_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    # TODO Resource is M2M field
    resource = forms.CharField(required=False, help_text='E.g. links to online catalogues.')
    resource_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    editors_notes = forms.CharField(required=False)
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    # TODO There is no images field in database model
    images = forms.CharField(required=False)
    images_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    last_edit_from = forms.CharField(required=False)
    last_edit_to = forms.CharField(required=False)
    last_edit_info = "Enter as dd/mm/yyyy hh:mm or dd/mm/yyyy (please note: dd/mm/yyyy counts as the very " \
                     "start of a day)."

    change_user = forms.CharField(required=False, help_text='Username of the person who last changed the record.')
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    institution_id = forms.IntegerField(required=False, min_value=1,
                                        help_text='The unique ID for the record within this database.')
    institution_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
