import logging
import os
import time
from datetime import datetime
from zipfile import BadZipFile

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.utils import timezone
from pandas._config.config import OptionError

from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_PEOPLE_MENTIONED_IN_WORK, \
    REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_STORED_IN, REL_TYPE_IS_RELATED_TO
from core.models import CofkUnionResource
from institution.models import CofkCollectInstitution, CofkUnionInstitution
from location.models import CofkCollectLocation, CofkUnionLocation
from manifestation.models import CofkCollectManifestation, CofkUnionManifestation, CofkManifInstMap
from person.models import CofkCollectPerson, CofkUnionPerson
from uploader.forms import CofkCollectUploadForm
from django.conf import settings

from uploader.models import CofkCollectStatus, CofkCollectUpload
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.validation import CofkMissingColumnError, CofkMissingSheetError, CofkNoDataError

from work.models import CofkCollectWork, CofkCollectAuthorOfWork, CofkCollectAddresseeOfWork, CofkCollectLanguageOfWork, \
    CofkCollectPersonMentionedInWork, CofkCollectWorkResource, CofkUnionWork, CofkWorkPersonMap, \
    CofkCollectDestinationOfWork, CofkCollectOriginOfWork, CofkWorkLocationMap, CofkUnionLanguageOfWork, \
    CofkWorkResourceMap

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

        try:
            file = default_storage.open(new_upload.upload_file.name, 'rb')
        except OSError as oe:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': [oe]}}
            log.error(context['report']['errors'])
            return
        except Exception as e:
            context['report']['total_errors'] = 1
            context['error'] = 'Indeterminate error.'
            log.error(e)
            return

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
        # except KeyError as ke:
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
            # log.error(ve.args[0])
            log.error([err for i, err in enumerate(cmce.args[0]) if i % 2 != 0])
        except (FileNotFoundError, BadZipFile, OptionError, OSError) as e:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': ['Could not read the Excel file.']}}
            log.error(e)
        except ValueError as ve:
            context['report']['total_errors'] = 1
            context['report']['errors'] = {'file': {'total': 1, 'error': [ve]}}
            log.error(ve)
        # except Exception as e:
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


def create_union_work(collect_work: CofkCollectWork):
    union_dict = {
        # work_id is primary key in CofkUnionWork
        'work_id': f'work_{datetime.now().strftime("%Y%m%d%H%M%S%f")}_{collect_work.iwork_id}',
    }

    for field in [f for f in collect_work._meta.get_fields() if f.name != 'iwork_id']:
        try:
            CofkUnionWork._meta.get_field(field.name)
            union_dict[field.name] = getattr(collect_work, field.name)

        except FieldDoesNotExist:
            # log.warning(f'Field {field} does not exist')
            pass

    union_work = CofkUnionWork(**union_dict)
    union_work.save()

    return union_work


def link_person_to_work(entities: QuerySet, relationship_type: str,
                        union_work: CofkUnionWork, work_id, request):
    for person in entities.filter(iwork_id=work_id).all():
        union_person = CofkUnionPerson.objects.filter(iperson_id=person.iperson.iperson_id).first()

        cwpm = CofkWorkPersonMap(relationship_type=relationship_type,
                                 work=union_work, person=union_person, person_id=union_person.person_id)
        cwpm.update_current_user_timestamp(request.user.username)
        cwpm.save()


def link_location_to_work(entities: QuerySet, relationship_type: str,
                          union_work: CofkUnionWork, work_id, request):
    for destination in entities.filter(iwork_id=work_id).all():
        union_location = CofkUnionLocation.objects.filter(location_id=destination.location.location_id).first()

        cwlm = CofkWorkLocationMap(relationship_type=relationship_type,
                                   work=union_work, location=union_location, location_id=union_location.location_id)
        cwlm.update_current_user_timestamp(request.user.username)
        cwlm.save()


def create_union_manifestations(work_id: str, union_work: CofkUnionWork, request, context):
    for manif in context['manifestations'].filter(iwork_id=work_id).all():
        union_dict = {'manifestation_creation_date_is_range': 0}
        for field in [f for f in manif._meta.get_fields() if f.name != 'iwork_id']:
            try:
                CofkUnionManifestation._meta.get_field(field.name)
                union_dict[field.name] = getattr(manif, field.name)

            except FieldDoesNotExist:
                # log.warning(f'Field {field} does not exist')
                pass

        union_manif = CofkUnionManifestation(**union_dict)
        union_manif.work = union_work
        union_manif.save()

        if manif.repository_id is not None:
            inst = context['institutions'].filter(id=manif.repository_id).first()
            union_inst = CofkUnionInstitution.objects.filter(pk=inst.institution_id).first()

            cmim = CofkManifInstMap(relationship_type=REL_TYPE_STORED_IN,
                                    manif=union_manif, inst=union_inst, inst_id=union_inst.institution_id)
            cmim.update_current_user_timestamp(request.user.username)
            cmim.save()


def accept_work(request, context: dict, upload: CofkCollectUpload):
    work_id = request.GET['work_id']
    collect_work = context['works'].filter(pk=work_id).first()

    if collect_work.upload_status_id != 1:
        return

    # Create work
    union_work = create_union_work(collect_work)

    # Link people
    link_person_to_work(entities=context['authors'], relationship_type=REL_TYPE_CREATED,
                        union_work=union_work, work_id=work_id, request=request)
    link_person_to_work(entities=context['addressees'], relationship_type=REL_TYPE_WAS_ADDRESSED_TO,
                        union_work=union_work, work_id=work_id, request=request)
    link_person_to_work(entities=context['mentioned'], relationship_type=REL_TYPE_PEOPLE_MENTIONED_IN_WORK,
                        union_work=union_work, work_id=work_id, request=request)

    # Link languages
    for lang in context['languages'].filter(iwork_id=work_id).all():
        CofkUnionLanguageOfWork(work=union_work, language_code=lang.language_code).save()

    # Link locations
    link_location_to_work(entities=context['destinations'], relationship_type=REL_TYPE_WAS_SENT_TO,
                          union_work=union_work, work_id=work_id, request=request)
    link_location_to_work(entities=context['origins'], relationship_type=REL_TYPE_WAS_SENT_FROM,
                          union_work=union_work, work_id=work_id, request=request)

    # Create manifestations
    create_union_manifestations(work_id=work_id, union_work=union_work,
                                request=request, context=context)

    # Link resources
    for resource in context['resources'].filter(iwork_id=work_id).all():
        union_resource = CofkUnionResource()
        union_resource.resource_url = resource.resource_url
        union_resource.resource_name = resource.resource_name
        union_resource.resource_details = resource.resource_details
        union_resource.resource_id = resource.resource_id
        union_resource.save()

        cwrm = CofkWorkResourceMap(relationship_type=REL_TYPE_IS_RELATED_TO,
                                   work=union_work, resource=union_resource, resource_id=union_resource.resource_id)
        cwrm.update_current_user_timestamp(request.user.username)
        cwrm.save()

    # Change state of upload and work
    upload.upload_status_id = 2  # Partly reviewed
    upload.works_accepted += 1
    upload.save()

    collect_work.upload_status_id = 4  # Accepted and saved into main database
    collect_work.save()


def reject_work(request, context: dict, upload: CofkCollectUpload):
    work_id = request.GET['work_id']
    collect_work = context['works'].filter(pk=work_id).first()

    if collect_work.upload_status_id != 1:
        return

    upload.upload_status_id = 2  # Partly reviewed
    upload.works_rejected += 1
    # upload.save()

    collect_work.upload_status_id = 5  # Rejected
    # collect_work.save()


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
               # Authors, addressees and mentioned link to People, here we're only
               # passing new people for review purposes
               'people': CofkCollectPerson.objects.filter(upload=upload, iperson_id__isnull=True),
               'places': CofkCollectLocation.objects.filter(upload=upload),
               'destinations': CofkCollectDestinationOfWork.objects.filter(upload=upload),
               'origins': CofkCollectOriginOfWork.objects.filter(upload=upload),
               'institutions': CofkCollectInstitution.objects.filter(upload=upload),
               'manifestations': CofkCollectManifestation.objects.filter(upload=upload),
               'resources': CofkCollectWorkResource.objects.filter(upload=upload)}

    if 'work_id' in request.GET:
        if 'accept_work' in request.GET:
            accept_work(request, context, upload)
        elif 'reject_work' in request.GET:
            reject_work(request, context, upload)

    return render(request, template_url, context)
