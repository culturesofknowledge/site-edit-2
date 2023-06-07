import logging
import os
import time
from zipfile import BadZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from core import constant
from core.models import CofkLookupCatalogue
from uploader.forms import CofkCollectUploadForm
from uploader.models import CofkCollectUpload, CofkCollectWork, CofkCollectAddresseeOfWork, CofkCollectAuthorOfWork, \
    CofkCollectDestinationOfWork, CofkCollectLanguageOfWork, CofkCollectOriginOfWork, CofkCollectPersonMentionedInWork, \
    CofkCollectWorkResource, CofkCollectInstitution, CofkCollectLocation, CofkCollectManifestation, CofkCollectPerson
from uploader.review import accept_works, reject_works, get_work
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.validation import CofkExcelFileError

log = logging.getLogger(__name__)


def handle_upload(request) -> dict:
    form = CofkCollectUploadForm(request.POST, request.FILES)
    report = {}

    if form.is_valid():
        start = time.time()
        new_upload = form.save(commit=False)
        new_upload.upload_status_id = 1
        new_upload.uploader_email = request.user.email
        new_upload.upload_timestamp = timezone.now()
        new_upload.save()

        try:
            file = default_storage.open(new_upload.upload_file.name, 'rb')
        except OSError as oe:
            report['total_errors'] = 1
            report['errors'] = {'file': {'total': 1, 'error': [oe]}}
            log.error(report['errors'])
            return report
        except Exception as e:
            report['total_errors'] = 1
            report['errors'] = 'Indeterminate error.'
            log.error(e)
            return report

        log.info(f'User: {request.user.username} uploaded file: "{file}" ({new_upload})')

        cuef = None
        report = {
            'file': request.FILES['upload_file']._name,
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

            report['elapsed'] = elapsed

        except CofkExcelFileError as cmce:
            errors = [str(cmce)]
            report['total_errors'] = len(errors)
            report['errors'] = {'file': {'total': len(errors), 'error': errors}}
            log.error(cmce.msg)
        except (FileNotFoundError, BadZipFile, OSError) as e:
            report['total_errors'] = 1
            report['errors'] = {'file': {'total': 1, 'error': ['Could not read the file.']}}
            log.error(e)
        except ValueError as ve:
            report['total_errors'] = 1
            report['errors'] = {'file': {'total': 1, 'error': [ve]}}
            log.error(ve)
        except Exception as e:
            report['total_errors'] = 1
            report['errors'] = 'Indeterminate error.'
            log.error(e)

        if cuef and cuef.errors:
            log.error(f'Deleting upload {new_upload}')
            new_upload.delete()
            # TODO delete uploaded file
            report['errors'] = cuef.errors
            report['total_errors'] = cuef.total_errors
        elif 'total_errors' in report:
            log.error(f'Deleting upload {new_upload}')
            new_upload.delete()
        else:
            new_upload.upload_name = request.FILES['upload_file']._name + ' ' + str(new_upload.upload_timestamp)
            new_upload.uploader_email = request.user.email
            new_upload.upload_username = f'{request.user.forename} {request.user.surname}'
            new_upload.save()
    else:
        report['errors'] = 'Form invalid'

    return report


@method_decorator([login_required,
                   permission_required(constant.PM_CHANGE_COLLECTWORK, raise_exception=True)],
                  name='dispatch')
class UploadView(ListView):
    model = CofkCollectUpload
    ordering = '-upload_timestamp'
    template_name = 'uploader/form.html'
    form = CofkCollectUploadForm
    paginate_by = 250

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form to create new upload
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        report = kwargs['report'] = handle_upload(request)

        # If workbook upload is successful redirect to review view
        if 'total_errors' not in report:
            return redirect(f'/upload/{report["upload_id"]}')

        return self.get(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)

        if kwargs:
            response.context_data |= kwargs

        return response

@login_required
@permission_required(constant.PM_CHANGE_COLLECTWORK, raise_exception=True)
def upload_review(request, upload_id, **kwargs):
    template_url = 'uploader/review.html'
    upload = CofkCollectUpload.objects.filter(upload_id=upload_id).first()

    works_paginator = Paginator(CofkCollectWork.objects.filter(upload=upload).order_by('pk'), 25)
    page_number = request.GET.get('page', 1)
    works_page = works_paginator.get_page(page_number)

    # TODO, are all of these required for context?
    context = {'upload': upload,
               'works_page': works_page,
               'authors': CofkCollectAuthorOfWork.objects.filter(upload=upload),
               'addressees': CofkCollectAddresseeOfWork.objects.filter(upload=upload),
               'mentioned': CofkCollectPersonMentionedInWork.objects.filter(upload=upload),
               'languages': CofkCollectLanguageOfWork.objects.filter(upload=upload),
               # Authors, addressees and mentioned link to People, here we're only
               # passing new people for review purposes
               'people': CofkCollectPerson.objects.filter(upload=upload, iperson_id__isnull=True),
               'places': CofkCollectLocation.objects.filter(upload=upload),
               'destinations': CofkCollectDestinationOfWork.objects.filter(upload=upload),
               'origins': CofkCollectOriginOfWork.objects.filter(upload=upload),
               'institutions': CofkCollectInstitution.objects.filter(upload=upload),
               'manifestations': CofkCollectManifestation.objects.filter(upload=upload),
               'resources': CofkCollectWorkResource.objects.filter(upload=upload)}

    if 'accept_all' in request.POST or 'accept_work' in request.POST:
        context['accept_work'] = True
        context['catalogues'] = CofkLookupCatalogue.objects.all()

        work_id = request.POST['work_id'] if 'work_id' in request.POST else None

        if work_id:
            context['work'] = get_work(context['works_page'].paginator.object_list, work_id)[0]
    elif 'confirm_accept' in request.POST:
        accept_works(request, context, upload)
    elif 'reject_all' in request.POST or 'reject_work' in request.POST:
        reject_works(request, context, upload)

    return render(request, template_url, context)
