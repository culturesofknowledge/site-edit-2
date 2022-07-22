import json
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

from institution.models import CofkCollectInstitution
from location.models import CofkCollectLocation
from manifestation.models import CofkCollectManifestation
from person.models import CofkCollectPerson
from uploader.forms import CofkCollectUploadForm
from django.conf import settings

from uploader.models import CofkCollectStatus, CofkCollectUpload
from uploader.spreadsheet import CofkUploadExcelFile
from work.forms import CofkCollectWorkForm
from work.models import CofkCollectWork

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
        context['report'] = {'file': request.FILES['upload_file']._name,
                             'time': new_upload.upload_timestamp,
                             'size': os.path.getsize(settings.MEDIA_ROOT + new_upload.upload_file.name) >> 10,
                             'upload_id': new_upload.upload_id, }

        try:
            cuef = CofkUploadExcelFile(new_upload, file)

            elapsed = round(time.time() - start)

            if not elapsed:
                elapsed = '1 second'
            else:
                elapsed = f'{elapsed + 1} seconds'

            context['report']['elapsed'] = elapsed

        except ValidationError as ve:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': str(ve)[1:-1]}}
            log.error(ve)
        except KeyError as ke:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': f'Column "{ke.args[0]}" missing'}}
            log.error(context['report']['error'])
        except ValueError as ve:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': ve.args[0]}}
            log.error(vars(ve))
        except (FileNotFoundError, BadZipFile, OptionError, OSError) as e:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': 'Could not read the Excel file.'}}
            log.error(e)
        #except Exception as e:
        #    context['report']['total_errors'] = 1
        #    context['error'] = 'Indeterminate error.'
        #    log.error(e)

        if cuef and cuef.errors:
            new_upload.delete()
            # TODO delete uploaded file
            context['report']['errors'] = cuef.errors
            context['report']['total_errors'] = cuef.total_errors
        elif context['report']['total_errors']:
            new_upload.delete()
        else:
            new_upload.upload_name = request.FILES['upload_file']._name + ' ' + str(new_upload.upload_timestamp)
            new_upload.uploader_email = request.user.email
            new_upload.upload_username = f'{request.user.forename} {request.user.surname}'
            new_upload.save()
    else:
        context['report'] = {'errors': 'Form invalid'}

    return context


@login_required
def upload_view(request, **kwargs):
    template_url = 'form.html'
    form = CofkCollectUploadForm
    context = {'form': form, }

    if request.method == 'POST':
        context = handle_upload(request, context)

        # If workbook upload is successful we redirect to review view
        if 'report' in context and 'total_errors' not in context['report']:
            print(context['report'])
            return redirect(f'/upload/{context["report"]["upload_id"]}')

    context['uploads'] = CofkCollectUpload.objects.all()

    return render(request, template_url, context)


@login_required
def upload_review(request, upload_id, **kwargs):
    template_url = 'review.html'
    upload = CofkCollectUpload.objects.filter(upload_id=upload_id).first()
    # works = [CofkCollectWorkForm(instance=w) for w in CofkCollectWork.objects.filter(upload=upload)]
    work_form = 0 # CofkCollectWorkForm(instance=works[0])

    context = {'upload': upload,
               'works': CofkCollectWork.objects.filter(upload=upload),
               'people': CofkCollectPerson.objects.filter(upload=upload),
               'places': CofkCollectLocation.objects.filter(upload=upload),
               'institutions': CofkCollectInstitution.objects.filter(upload=upload),}
               #'manifestations': CofkCollectManifestation.objects.filter(upload=upload)}

    return render(request, template_url, context)