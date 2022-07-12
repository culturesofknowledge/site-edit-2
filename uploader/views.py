import logging
import os
import time

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.utils import timezone

from uploader.forms import CofkCollectUploadForm
from django.conf import settings

from uploader.models import CofkCollectStatus
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.validation import CofkExcelFileError

log = logging.getLogger(__name__)


@login_required
def upload_view(request, **kwargs):
    template_url = 'form.html'
    form = CofkCollectUploadForm
    context = {'form': form,
               'errors': []}

    if request.method == 'POST':
        form = CofkCollectUploadForm(request.POST, request.FILES)

        if form.is_valid():
            start = time.time()
            new_upload = form.save(commit=False)
            new_upload.upload_status = CofkCollectStatus.objects.filter(status_id=1).first()
            new_upload.upload_timestamp = timezone.now()
            new_upload.total_works = 0
            new_upload.works_accepted = 0
            new_upload.works_rejected = 0
            new_upload.save()

            file = default_storage.open(new_upload.upload_file.name, 'rb')

            cuef = None

            # try:
            cuef = CofkUploadExcelFile(new_upload, file)
            '''except CofkExcelFileError as cefe:
                context['errors'] += cefe.errors
                log.error(cefe.msg)
                log.error(cefe.errors)
            except (FileNotFoundError, ValueError) as e:
                context['errors'].append(e)
                log.error(e)
            '''

            if not cuef:
                new_upload.delete()
            else:
                context['report'] = {'file': request.FILES['upload_file']._name,
                                     'size': os.path.getsize(settings.MEDIA_ROOT + new_upload.upload_file.name) >> 10,
                                     'elapsed': round(time.time() - start),
                                     'report': cuef.report}

    return render(request, template_url, context)
