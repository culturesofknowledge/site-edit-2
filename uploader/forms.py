from django import forms

from uploader.models import CofkCollectUpload, CofkCollectWork

excelMimeTypes = ".xls," \
                 ".xlsx," \
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet," \
                 "application/vnd.ms-excel"


class CofkCollectUploadForm(forms.ModelForm):
    class Meta:
        model = CofkCollectUpload
        fields = ('upload_file', )
        # exclude = ['_id']
        widgets = {
            'upload_file': forms.FileInput(attrs={'accept': excelMimeTypes,
                                                  'class': 'btn'})
        }


class CofkCollectWorkForm(forms.ModelForm):
    class Meta:
        model = CofkCollectWork
        fields = '__all__'
        # exclude = ['_id']
