import logging
from datetime import datetime
from typing import List, Type

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, models
from django.db.models import QuerySet

from cllib_django import email_utils
from django.urls import reverse

from core.constant import REL_TYPE_STORED_IN, REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, \
    REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_IS_RELATED_TO, \
    REL_TYPE_MENTION, REL_TYPE_DEALS_WITH
from core.models import CofkUnionResource, CofkLookupCatalogue
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation import manif_serv
from manifestation.models import CofkUnionManifestation, CofkManifInstMap
from person.models import CofkUnionPerson, create_person_id
from uploader.models import CofkCollectUpload, CofkCollectWork
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkPersonMap, CofkWorkResourceMap, \
    CofkUnionLanguageOfWork, CofkWorkSubjectMap

log = logging.getLogger(__name__)


def create_union_work(union_work_dict: dict, collect_work: CofkCollectWork):
    # work_id is primary key in CofkUnionWork
    # note that work_serv.create_work_id uses a different less detailed format
    union_work_dict['work_id'] = f'work_{datetime.now().strftime("%Y%m%d%H%M%S%f")}_{collect_work.iwork_id}'
    exclude = ['iwork_id', 'subjects']

    for field in [f for f in collect_work._meta.get_fields() if f.name not in exclude]:
        try:
            CofkUnionWork._meta.get_field(field.name)

            if value := getattr(collect_work, field.name):
                union_work_dict[field.name] = value

        except FieldDoesNotExist:
            # log.warning(f'Field {field} does not exist')
            pass

    return CofkUnionWork(**union_work_dict)


def link_person_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, username: str) \
        -> List[CofkWorkPersonMap]:
    person_maps = []
    for person in entities.all():
        if person.iperson.union_iperson is None:
            union_iperson = CofkUnionPerson(foaf_name=person.iperson.primary_name)
            union_iperson.person_id = create_person_id(union_iperson.iperson_id)
            union_iperson.save()
            person.iperson.union_iperson = union_iperson
            log.info(f'Created new union person {union_iperson}')

        cwpm = CofkWorkPersonMap(relationship_type=relationship_type,
                                 work=union_work, person=person.iperson.union_iperson,
                                 person_id=person.iperson.union_iperson.person_id)
        cwpm.update_current_user_timestamp(username)
        person_maps.append(cwpm)

    return person_maps


def link_location_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, username: str) \
        -> List[CofkWorkLocationMap]:
    location_maps = []
    for origin_or_dest in entities.all():
        if origin_or_dest.location.union_location is None:
            union_location = CofkUnionLocation(location_name=origin_or_dest.location.location_name)
            union_location.save()
            origin_or_dest.location.union_location = union_location
            log.info(f'Created new union location {union_location}')

        cwlm = CofkWorkLocationMap(relationship_type=relationship_type,
                                   work=union_work, location=origin_or_dest.location.union_location,
                                   location_id=origin_or_dest.location.union_location.location_id)
        cwlm.update_current_user_timestamp(username)
        location_maps.append(cwlm)

    return location_maps


def bulk_create(objects: List[Type[models.Model]]):
    if objects:
        try:
            type(objects[0]).objects.bulk_create(objects, batch_size=500)
        except IntegrityError as ie:
            log.error(ie)
            log.exception(ie)
            # self.add_error(f'Could not create {type(objects[0])} objects in database.')


def add_rel_maps(rel_maps: dict, entity_maps: List):
    if not len(entity_maps):
        return

    if str(type(entity_maps[0])) not in rel_maps:
        rel_maps[str(type(entity_maps[0]))] = []

    rel_maps[str(type(entity_maps[0]))] += entity_maps


def accept_works(context: dict, upload: CofkCollectUpload, request=None, email_addresses: List[str] = None):
    filter_args = {'upload_status_id': 1}

    if 'work_id' in context and context['work_id'] != 'all':
        filter_args['iwork_id'] = context['work_id']

    collect_works = context['works_page'].paginator.object_list.filter(**filter_args)

    if not collect_works:
        msg = f'No works in the upload "{upload.upload_name}" can be accepted (was the page refreshed?).'
        if request:
            messages.error(request, msg)
        else:
            email_utils.send_email(email_addresses,
                                   subject='EMLO Works Accepted Result',
                                   content=msg)
        return msg

    union_works = []
    union_manifs = []
    union_resources = []
    rel_maps = {}
    username = context['username']

    union_work_dict = {'accession_code': context['accession_code'] if 'accession_code' in context else None}

    if 'catalogue_code' in context and context['catalogue_code'] != '':
        union_work_dict['original_catalogue'] = CofkLookupCatalogue.objects \
            .filter(catalogue_code=context['catalogue_code']).first()

    for collect_work in collect_works:
        # Create work
        union_work = create_union_work(union_work_dict, collect_work)
        union_works.append(union_work)

        # Link people
        people_maps = link_person_to_work(entities=collect_work.authors, relationship_type=REL_TYPE_CREATED,
                                          union_work=union_work, username=username)
        people_maps += link_person_to_work(entities=collect_work.addressees,
                                           relationship_type=REL_TYPE_WAS_ADDRESSED_TO, union_work=union_work,
                                           username=username)
        people_maps += link_person_to_work(entities=collect_work.people_mentioned,
                                           relationship_type=REL_TYPE_MENTION,
                                           union_work=union_work, username=username)
        add_rel_maps(rel_maps, people_maps)

        # Link languages
        lang_maps = [CofkUnionLanguageOfWork(work=union_work, language_code=lang.language_code) for
                     lang in collect_work.languages.all()]
        add_rel_maps(rel_maps, lang_maps)

        subj_maps = []
        # Link subjects
        for s in collect_work.subjects.all():
            cwss = CofkWorkSubjectMap(work=union_work, subject=s.subject, relationship_type=REL_TYPE_DEALS_WITH)
            cwss.update_current_user_timestamp(username)
            subj_maps.append(cwss)

        add_rel_maps(rel_maps, subj_maps)

        # Link locations
        loc_maps = link_location_to_work(entities=collect_work.destination, relationship_type=REL_TYPE_WAS_SENT_TO,
                                         union_work=union_work, username=username)
        loc_maps += link_location_to_work(entities=collect_work.origin, relationship_type=REL_TYPE_WAS_SENT_FROM,
                                          union_work=union_work, username=username)
        add_rel_maps(rel_maps, loc_maps)

        union_maps = []

        for manif in collect_work.manifestations.all():
            union_manif_dict = {'manifestation_id': manif_serv.create_manif_id(union_work.iwork_id),
                                'work': union_work}
            for field in [f for f in manif._meta.get_fields() if f.name != 'manifestation_id']:
                try:
                    CofkUnionManifestation._meta.get_field(field.name)
                    union_manif_dict[field.name] = getattr(manif, field.name)

                except FieldDoesNotExist:
                    # log.warning(f'Field {field} does not exist')
                    pass

            union_manif = CofkUnionManifestation(**union_manif_dict)
            union_manifs.append(union_manif)

            if manif.repository_id is not None:
                inst = manif.repository
                union_inst = CofkUnionInstitution.objects.filter(pk=inst.institution_id).first()

                cmim = CofkManifInstMap(relationship_type=REL_TYPE_STORED_IN,
                                        manif=union_manif, inst=union_inst, inst_id=union_inst.institution_id)
                cmim.update_current_user_timestamp(username)
                union_maps.append(cmim)

        add_rel_maps(rel_maps, union_maps)

        res_maps = []

        # Link resources
        for resource in collect_work.resources.all():
            union_resource = CofkUnionResource()
            union_resource.resource_url = resource.resource_url
            union_resource.resource_name = resource.resource_name
            union_resource.resource_details = resource.resource_details
            union_resources.append(union_resource)

            cwrm = CofkWorkResourceMap(relationship_type=REL_TYPE_IS_RELATED_TO, work=union_work,
                                       resource=union_resource, resource_id=union_resource.resource_id)
            cwrm.update_current_user_timestamp(username)
            res_maps.append(cwrm)

        add_rel_maps(rel_maps, res_maps)

        collect_work.upload_status_id = 4  # Accepted and saved into main database

    log_msg = []

    # Creating the union entities
    for entity in [union_works, union_manifs, union_resources]:
        if len(entity) > 0:
            bulk_create(entity)
            log_msg.append(f'{len(entity)} {type(entity[0]).__name__}')

    # Creating the relation entities
    for rel_map in rel_maps:
        if len(rel_maps[rel_map]) > 0:
            bulk_create(rel_maps[rel_map])
            log_msg.append(f'{len(rel_maps[rel_map])} {type(rel_maps[rel_map][0]).__name__}')

    # Update upload status of collect works
    CofkCollectWork.objects.bulk_update(collect_works, ['upload_status'])

    accepted_works = len(collect_works)

    if accepted_works > 1:
        msg = f'Successfully accepted {accepted_works} works.'
    else:
        msg = 'Successfully accepted one work.'

    # Change state of upload and work
    upload.works_accepted += accepted_works

    if upload.total_works == upload.works_accepted + upload.works_rejected:
        upload.upload_status_id = 3  # Review complete
    else:
        upload.upload_status_id = 2  # Partly reviewed

    upload.save()

    if request:
        messages.success(request, msg)
    else:
        url = settings.UPLOAD_ROOT_URL + reverse('uploader:upload_works') + f'?upload_id={upload.pk}'
        msg = (f'The upload "{upload.upload_name}" has been successfully processed.\n{msg}\n'
               f'Click here: {url}')
        email_utils.send_email(upload.uploader_email,
                               subject='EMLO Works Accepted Result',
                               content=msg)

    log.info(f'{upload}: created ' + ', '.join(log_msg))


def reject_works(context: dict, upload: CofkCollectUpload, request):
    filter_args = {'upload_status_id': 1}

    if 'work_id' in context and context['work_id'] != 'all':
        filter_args['iwork_id'] = context['work_id']

    collect_works = context['works_page'].paginator.object_list.filter(**filter_args)

    if not collect_works:
        msg = f'No works in the upload "{upload.upload_name}" can be deleted (was the page refreshed?).'
        messages.error(request, msg)
        return

    for collect_work in collect_works:
        collect_work.upload_status_id = 5  # Rejected

    CofkCollectWork.objects.bulk_update(collect_works, ['upload_status_id'])

    # Change state of upload and work
    upload.works_rejected += len(collect_works)

    if upload.total_works == upload.works_accepted + upload.works_rejected:
        upload.upload_status_id = 3  # Review complete
    else:
        upload.upload_status_id = 2  # Partly reviewed

    upload.save()

    messages.success(request, f'Successfully rejected {len(collect_works)} work/s')
    log.info(f'{upload}: rejected {len(collect_works)}')
