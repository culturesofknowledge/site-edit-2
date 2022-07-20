import logging
import os
import time
from zipfile import BadZipFile

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.utils import timezone
from pandas._config.config import OptionError

from uploader.forms import CofkCollectUploadForm
from django.conf import settings

from uploader.models import CofkCollectStatus, CofkCollectUpload
from uploader.spreadsheet import CofkUploadExcelFile

log = logging.getLogger(__name__)


def handle_upload(request, context):
    form = CofkCollectUploadForm(request.POST, request.FILES)

    if form.is_valid():

        start = time.time()
        new_upload = form.save(commit=False)
        new_upload.upload_status = CofkCollectStatus.objects.filter(status_id=1).first()
        new_upload.upload_timestamp = timezone.now()
        new_upload.works_accepted = 0
        new_upload.works_rejected = 0
        new_upload.total_works = 0
        new_upload.save()

        file = default_storage.open(new_upload.upload_file.name, 'rb')

        cuef = None

        try:
            cuef = CofkUploadExcelFile(new_upload, file)

            elapsed = round(time.time() - start)

            if not elapsed:
                elapsed = '1 second'
            else:
                elapsed = f'{elapsed + 1} seconds'

            context['report'] = {'file': request.FILES['upload_file']._name,
                                 'time': new_upload.upload_timestamp,
                                 'size': os.path.getsize(settings.MEDIA_ROOT + new_upload.upload_file.name) >> 10,
                                 'elapsed': elapsed,
                                 'summary': cuef.summary,
                                 'upload_id': new_upload.upload_id, }
        except ValidationError as ve:
            context['error'] = str(ve)[1:-1]
            log.error(ve)
        except KeyError as ke:
            context['error'] = f'Column "{ke.args[0]}" missing'
            log.error(context['error'])
        except ValueError as ve:
            context['error'] = ve.args[0]
            log.error(vars(ve))
        except (FileNotFoundError, BadZipFile, OptionError, OSError) as e:
            context['error'] = 'Could not read the Excel file.'
            log.error(e)
        #except Exception as e:
        #    context['error'] = 'Indeterminate error.'
        #    log.error(e)

        if not cuef:
            new_upload.delete()
        else:
            new_upload.upload_name = request.FILES['upload_file']._name + ' ' + str(new_upload.upload_timestamp)
            new_upload.uploader_email = request.user.email
            new_upload.save()

        return context


@login_required
def upload_view(request, **kwargs):
    template_url = 'form.html'
    form = CofkCollectUploadForm
    context = {'form': form, }

    if request.method == 'POST':
        context = handle_upload(request, context)

        if 'report' in context and context['report']['total_errors'] == 0:
            return redirect(f'/upload/{context["report"]["upload_id"]}')

    else:
        context['uploads'] = CofkCollectUpload.objects.all()

    return render(request, template_url, context)


@login_required
def upload_review(request, **kwargs):
    template_url = 'review.html'
    context = {}

    return render(request, template_url, context)