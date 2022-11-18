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
from uploader.validation import CofkMissingColumnError, CofkMissingSheetError, CofkNoDataError

from work.models import CofkCollectWork, CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, CofkCollectLanguageOfWork, \
    CofkCollectPersonMentionedInWork, CofkCollectWorkResource

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
            context['report']['errors'] = {'file': {'total': 1, 'error': [str(ve)[1:-1]]}}
            log.error(ve)
        #except KeyError as ke:
        #    context['report']['total_errors'] = 1
        #    context['report']['errors'] = {'file': {'total': 1, 'error': [f'Column "{ke.args[0]}" missing']}}
        #    log.error(context['report']['errors'])
        except CofkNoDataError as cnde:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': [cnde]}}
            log.error(context['report']['errors'])
        except CofkMissingSheetError as cmse:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': [cmse]}}
            log.error(context['report']['errors'])
        except CofkMissingColumnError as cmce:
            errors = [str(err) for i, err in enumerate(cmce.args[0]) if i % 2 != 0]
            context['report']['total_errors'] = len(errors)
            context['report']['errors'] = {'file': {'total': len(errors), 'error': errors}}
            #log.error(ve.args[0])
            log.error([err for i, err in enumerate(cmce.args[0]) if i % 2 != 0])
        except (FileNotFoundError, BadZipFile, OptionError, OSError) as e:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': ['Could not read the Excel file.']}}
            log.error(e)
        #except Exception as e:
        #    context['report']['total_errors'] = 1
        #    context['error'] = 'Indeterminate error.'
        #    log.error(e)

        if cuef and cuef.errors:
            log.error('Deleting new upload')
            new_upload.delete()
            # TODO delete uploaded file
            context['report']['errors'] = cuef.errors
            context['report']['total_errors'] = cuef.total_errors
        elif 'total_errors' in context['report']:
            log.error('Deleting new upload')
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
    template_url = 'uploader/form.html'
    form = CofkCollectUploadForm
    context = {'form': form, }

    if request.method == 'POST':
        context = handle_upload(request, context)

        # If workbook upload is successful we redirect to review view
        if 'report' in context and 'total_errors' not in context['report']:
            return redirect(f'/upload/{context["report"]["upload_id"]}')

    context['uploads'] = CofkCollectUpload.objects.order_by('-upload_timestamp').all()

    return render(request, template_url, context)


@login_required
def upload_review(request, upload_id, **kwargs):
    template_url = 'uploader/review.html'
    upload = CofkCollectUpload.objects.filter(upload_id=upload_id).first()

    context = {'upload': upload,
               'works': CofkCollectWork.objects.filter(upload=upload),
               'authors': CofkCollectAuthorOfWork.objects.filter(upload=upload),
               'addressees': CofkCollectAddresseeOfWork.objects.filter(upload=upload),
               'mentioned': CofkCollectPersonMentionedInWork.objects.filter(upload=upload),
               'languages': CofkCollectLanguageOfWork.objects.filter(upload=upload),
               # Authors, addressees and mentinoed link to People, here we're only
               # passing new people for review purposes
               'people': CofkCollectPerson.objects.filter(upload=upload, iperson_id__isnull=True),
               'places': CofkCollectLocation.objects.filter(upload=upload),
               'institutions': CofkCollectInstitution.objects.filter(upload=upload),
               'manifestations': CofkCollectManifestation.objects.filter(upload=upload),
               'resources': CofkCollectWorkResource.objects.filter(upload=upload)}

    return render(request, template_url, context)
