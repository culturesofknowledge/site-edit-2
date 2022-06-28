import logging

from django.core.files.storage import default_storage
from django.shortcuts import render


from uploader.forms import CofkCollectUploadForm
from django.conf import settings

from uploader.models import CofkCollectStatus
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.validation import CofkExcelFileError

log = logging.getLogger(__name__)


def upload_view(request, **kwargs):
    template_url = 'form.html'
    form = CofkCollectUploadForm
    context = {'form': form,
               'errors': []}

    if request.method == 'POST':
        form = CofkCollectUploadForm(request.POST, request.FILES)

        if form.is_valid():
            new_upload = form.save(commit=False)
            new_upload.upload_status = CofkCollectStatus.objects.filter(status_id=1).first()
            new_upload.save()
            file = default_storage.open(new_upload.upload_file.name, 'rb')

            cuef = None

            try:
                cuef = CofkUploadExcelFile(new_upload, file)
            except CofkExcelFileError as cefe:
                context['errors'] += cefe.errors
                log.error(cefe.msg)
                log.error(cefe.errors)
            except FileNotFoundError as fnfe:
                context['errors'].append(fnfe)
                log.error(fnfe)
            except ValueError as ve:
                context['errors'].append(ve)
                log.error(ve)

            if not cuef:
                new_upload.delete()

    return render(request, template_url, context)
