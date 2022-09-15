from django import forms
from django.forms import ModelForm

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

