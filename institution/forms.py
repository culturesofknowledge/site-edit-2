from django import forms
from django.forms import ModelForm

from core.helper import form_utils
from institution.models import CofkUnionInstitution


class InstitutionForm(ModelForm):
    institution_name = forms.CharField()
    institution_city = forms.CharField()
    institution_country = forms.CharField()

    class Meta:
        model = CofkUnionInstitution
        exclude = (
            'creation_user',
            'change_user'
        )


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'institution/component/institution_search_fieldset.html'

    institution_id = forms.IntegerField(required=False, min_value=1)
    institution_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
