import logging
from datetime import datetime
from typing import List, Type

from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, models
from django.db.models import QuerySet

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


def link_person_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, work_id, request) \
        -> List[CofkWorkPersonMap]:
    person_maps = []
    for person in entities.filter(iwork_id=work_id).all():
        if person.iperson.union_iperson is None:
            union_iperson = CofkUnionPerson(foaf_name=person.iperson.primary_name)
            union_iperson.person_id = create_person_id(union_iperson.iperson_id)
            union_iperson.save()
            person.iperson.union_iperson = union_iperson
            log.info(f'Created new union person {union_iperson}')

        cwpm = CofkWorkPersonMap(relationship_type=relationship_type,
                                 work=union_work, person=person.iperson.union_iperson,
                                 person_id=person.iperson.union_iperson.person_id)
        cwpm.update_current_user_timestamp(request.user.username)
        person_maps.append(cwpm)

    return person_maps


def link_location_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, work_id, request) \
        -> List[CofkWorkLocationMap]:
    location_maps = []
    for origin_or_dest in entities.filter(iwork_id=work_id).all():
        if origin_or_dest.location.union_location is None:
            union_location = CofkUnionLocation(location_name=origin_or_dest.location.location_name)
            union_location.save()
            origin_or_dest.location.union_location = union_location
            log.info(f'Created new union location {union_location}')

        cwlm = CofkWorkLocationMap(relationship_type=relationship_type,
                                   work=union_work, location=origin_or_dest.location.union_location,
                                   location_id=origin_or_dest.location.union_location.location_id)
        cwlm.update_current_user_timestamp(request.user.username)
        location_maps.append(cwlm)

    return location_maps


def create_union_manifestations(work_id: int, union_work: CofkUnionWork, request, context) -> List[CofkManifInstMap]:
    union_maps = []
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
            union_maps.append(cmim)

    return union_maps


def bulk_create(objects: List[Type[models.Model]]):
    if objects:
        try:
            type(objects[0]).objects.bulk_create(objects, batch_size=500)
        except IntegrityError as ie:
            log.error(ie)
            log.exception(ie)
            # self.add_error(f'Could not create {type(objects[0])} objects in database.')


def get_work(works, work_id) -> list[CofkCollectWork] | None:
    try:
        work_id = int(work_id)
    except ValueError:
        return

    try:
        return [w for w in works if w.id == work_id]
    except IndexError:
        pass


def accept_works(request, context: dict, upload: CofkCollectUpload):
    collect_works = context['works_page'].paginator.object_list

    if 'work_id' in request.POST:
        collect_works = get_work(collect_works, request.POST['work_id'])

    # Skip any works that have already been reviewed
    collect_works = [c for c in collect_works if c.upload_status_id == 1]

    if not collect_works:
        messages.error(request, 'No works in upload can be accepted.')
        return

    union_works = []
    union_manifs = []
    union_resources = []
    rel_maps = []

    union_work_dict = {'accession_code': request.POST['accession_code'] if 'accession_code' in request.POST else None}

    if 'catalogue_code' in request.POST and request.POST['catalogue_code'] != '':
        union_work_dict['original_catalogue'] = CofkLookupCatalogue.objects \
            .filter(catalogue_code=request.POST['catalogue_code']).first()

    for collect_work in collect_works:
        work_id = collect_work.pk

        # Create work
        union_work = create_union_work(union_work_dict, collect_work)
        union_works.append(union_work)

        # Link people
        people_maps = link_person_to_work(entities=context['authors'], relationship_type=REL_TYPE_CREATED,
                                          union_work=union_work, work_id=work_id, request=request)
        people_maps += link_person_to_work(entities=context['addressees'], relationship_type=REL_TYPE_WAS_ADDRESSED_TO,
                                           union_work=union_work, work_id=work_id, request=request)
        people_maps += link_person_to_work(entities=context['mentioned'],
                                           relationship_type=REL_TYPE_MENTION,
                                           union_work=union_work, work_id=work_id, request=request)
        rel_maps.append(people_maps)

        # Link languages
        lang_maps = [CofkUnionLanguageOfWork(work=union_work, language_code=lang.language_code) for
                     lang in context['languages'].filter(iwork_id=work_id).all()]

        rel_maps.append(lang_maps)

        # Link subjects
        rel_maps.append([CofkWorkSubjectMap(work=union_work, subject=s.subject, relationship_type=REL_TYPE_DEALS_WITH)
                         for s in context['subjects'].filter(iwork_id=work_id).all()])

        # Link locations
        loc_maps = link_location_to_work(entities=context['destinations'], relationship_type=REL_TYPE_WAS_SENT_TO,
                                         union_work=union_work, work_id=work_id, request=request)
        loc_maps += link_location_to_work(entities=context['origins'], relationship_type=REL_TYPE_WAS_SENT_FROM,
                                          union_work=union_work, work_id=work_id, request=request)
        rel_maps.append(loc_maps)

        union_maps = []

        for manif in context['manifestations'].filter(iwork_id=work_id).all():
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
                inst = context['institutions'].filter(id=manif.repository_id).first()
                union_inst = CofkUnionInstitution.objects.filter(pk=inst.institution_id).first()

                cmim = CofkManifInstMap(relationship_type=REL_TYPE_STORED_IN,
                                        manif=union_manif, inst=union_inst, inst_id=union_inst.institution_id)
                cmim.update_current_user_timestamp(request.user.username)
                union_maps.append(cmim)

        rel_maps.append(union_maps)

        res_maps = []

        # Link resources
        for resource in context['resources'].filter(iwork_id=work_id).all():
            union_resource = CofkUnionResource()
            union_resource.resource_url = resource.resource_url
            union_resource.resource_name = resource.resource_name
            union_resource.resource_details = resource.resource_details
            union_resources.append(union_resource)

            cwrm = CofkWorkResourceMap(relationship_type=REL_TYPE_IS_RELATED_TO, work=union_work,
                                       resource=union_resource, resource_id=union_resource.resource_id)
            cwrm.update_current_user_timestamp(request.user.username)
            res_maps.append(cwrm)

        rel_maps.append(res_maps)

        collect_work.upload_status_id = 4  # Accepted and saved into main database

    log_msg = []

    # Creating the union entities
    for entity in [union_works, union_manifs, union_resources]:
        if len(entity) > 0:
            bulk_create(entity)
            log_msg.append(f'{len(entity)} {type(entity[0]).__name__}')

    # Creating the relation entities
    for rel_map in rel_maps:
        bulk_create(rel_map)

    # Update upload status of collect works
    CofkCollectWork.objects.bulk_update(collect_works, ['upload_status'])

    accepted_works = len(collect_works)

    # Change state of upload and work
    upload.works_accepted += accepted_works

    if upload.total_works == upload.works_accepted + upload.works_rejected:
        upload.upload_status_id = 3  # Review complete
    else:
        upload.upload_status_id = 2  # Partly reviewed

    upload.save()

    if accepted_works > 1:
        messages.success(request, f'Successfully accepted {accepted_works} works.')
    else:
        messages.success(request, f'Successfully accepted one work.')

    log.info(f'{upload}: created ' + ', '.join(log_msg))


def reject_works(request, context: dict, upload: CofkCollectUpload):
    collect_works = context['works_page'].paginator.object_list

    if 'work_id' in request.POST:
        collect_works = get_work(collect_works, request.GET['work_id'])

    # Skip any works that have already been reviewed
    collect_works = [c for c in collect_works if c.upload_status_id == 1]

    if not collect_works:
        messages.error(request, 'No works in upload can be deleted.')
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

    log.info(f'{upload}: rejected {len(collect_works)}')
