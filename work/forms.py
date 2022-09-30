from django import forms

from work.models import CofkCollectWork, CofkUnionWork


class CofkCollectWorkForm(forms.ModelForm):
    class Meta:
        model = CofkCollectWork
        fields = '__all__'
        # exclude = ['_id']


class WorkForm(forms.ModelForm):
    class Meta:
        model = CofkUnionWork
        fields = (
            'description',
        )
