from django import forms

from uploader.models import CofkCollectUpload


class CofkCollectUploadForm(forms.ModelForm):
    class Meta:
        model = CofkCollectUpload
        fields = ('upload_file', )
        # exclude = ['_id']
