from django import forms

from uploader.models import CofkCollectUpload

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
            'upload_file': forms.FileInput(attrs={'accept': excelMimeTypes})
        }
