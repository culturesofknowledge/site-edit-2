import logging
from datetime import datetime
from typing import List, Type

from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, models
from django.db.models import QuerySet

from core.constant import REL_TYPE_STORED_IN, REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, \
    REL_TYPE_PEOPLE_MENTIONED_IN_WORK, REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_IS_RELATED_TO
from core.models import CofkUnionResource
from institution.models import CofkUnionInstitution
from manifestation.models import CofkUnionManifestation, CofkManifInstMap
from uploader.models import CofkCollectUpload, CofkCollectWork
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkPersonMap, CofkWorkResourceMap, \
    CofkUnionLanguageOfWork, CofkUnionQueryableWork

log = logging.getLogger(__name__)


def create_union_work(collect_work: CofkCollectWork):
    union_dict = {
        # work_id is primary key in CofkUnionWork
        'work_id': f'work_{datetime.now().strftime("%Y%m%d%H%M%S%f")}_{collect_work.iwork_id}',
    }

    for field in [f for f in collect_work._meta.get_fields() if f.name != 'iwork_id']:
        try:
            CofkUnionWork._meta.get_field(field.name)

            if value := getattr(collect_work, field.name):
                union_dict[field.name] = value

        except FieldDoesNotExist:
            # log.warning(f'Field {field} does not exist')
            pass

    return CofkUnionWork(**union_dict)


def link_person_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, work_id, request) \
        -> List[CofkWorkPersonMap]:
    person_maps = []
    for person in entities.filter(iwork_id=work_id).all():
        cwpm = CofkWorkPersonMap(relationship_type=relationship_type,
                                 work=union_work, person=person.iperson.union_iperson,
                                 person_id=person.iperson.union_iperson.person_id)
        cwpm.update_current_user_timestamp(request.user.username)
        # cwpm.save()
        person_maps.append(cwpm)

    return person_maps


def link_location_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, work_id, request) \
        -> List[CofkWorkLocationMap]:
    location_maps = []
    for origin_or_dest in entities.filter(iwork_id=work_id).all():
        cwlm = CofkWorkLocationMap(relationship_type=relationship_type,
                                   work=union_work, location=origin_or_dest.location.union_location,
                                   location_id=origin_or_dest.location.union_location.location_id)
        cwlm.update_current_user_timestamp(request.user.username)
        # cwlm.save()
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
            # cmim.save()

    return union_maps


def bulk_create(objects: List[Type[models.Model]]):
    if objects:
        try:
            type(objects[0]).objects.bulk_create(objects, batch_size=500)
        except IntegrityError as ie:
            log.error(ie)
            log.exception(ie)
            # self.add_error(f'Could not create {type(objects[0])} objects in database.')


def get_work(works, work_id) -> CofkCollectWork | None:
    try:
        work_id = int(work_id)
    except ValueError:
        return

    try:
        return [w for w in works  if w.id == work_id][0]
    except IndexError:
        pass


# TODO refactor accept_work and accept_works common functionality
def accept_work(request, context: dict, upload: CofkCollectUpload):
    collect_work = get_work(context['works_page'].object_list, request.GET['work_id'])

    if not collect_work or collect_work.upload_status_id != 1:
        return

    work_id = collect_work.pk

    # Create work
    union_work = create_union_work(collect_work)
    union_work.save()

    # Link people
    people_maps = link_person_to_work(entities=context['authors'], relationship_type=REL_TYPE_CREATED,
                                      union_work=union_work, work_id=work_id, request=request)
    people_maps += link_person_to_work(entities=context['addressees'], relationship_type=REL_TYPE_WAS_ADDRESSED_TO,
                                       union_work=union_work, work_id=work_id, request=request)
    people_maps += link_person_to_work(entities=context['mentioned'],
                                       relationship_type=REL_TYPE_PEOPLE_MENTIONED_IN_WORK,
                                       union_work=union_work, work_id=work_id, request=request)
    bulk_create(people_maps)

    lang_maps = [CofkUnionLanguageOfWork(work=union_work, language_code=lang.language_code) for
                 lang in context['languages'].filter(iwork_id=work_id).all()]
    # Link languages
    bulk_create(lang_maps)

    # Link locations
    loc_maps = link_location_to_work(entities=context['destinations'], relationship_type=REL_TYPE_WAS_SENT_TO,
                          union_work=union_work, work_id=work_id, request=request)
    loc_maps += link_location_to_work(entities=context['origins'], relationship_type=REL_TYPE_WAS_SENT_FROM,
                          union_work=union_work, work_id=work_id, request=request)
    bulk_create(loc_maps)

    # Create manifestations
    union_maps = create_union_manifestations(work_id=work_id, union_work=union_work, request=request, context=context)
    bulk_create(union_maps)

    # Link resources
    for resource in context['resources'].filter(iwork_id=work_id).all():
        union_resource = CofkUnionResource()
        union_resource.resource_url = resource.resource_url
        union_resource.resource_name = resource.resource_name
        union_resource.resource_details = resource.resource_details
        union_resource.resource_id = resource.resource_id
        union_resource.save()

        cwrm = CofkWorkResourceMap(relationship_type=REL_TYPE_IS_RELATED_TO, work=union_work,
                                   resource=union_resource, resource_id=union_resource.resource_id)
        cwrm.update_current_user_timestamp(request.user.username)
        cwrm.save()

    # Change state of upload and work
    upload.upload_status_id = 2  # Partly reviewed
    upload.works_accepted += 1
    upload.save()

    collect_work.upload_status_id = 4  # Accepted and saved into main database
    collect_work.save()


def reject_work(request, context: dict, upload: CofkCollectUpload):
    collect_work = get_work(context['works_page'].object_list, request.GET['work_id'])

    if not collect_work or collect_work.upload_status_id != 1:
        return

    upload.upload_status_id = 2  # Partly reviewed
    upload.works_rejected += 1
    upload.save()

    collect_work.upload_status_id = 5  # Rejected
    collect_work.save()


def accept_works(request, context: dict, upload: CofkCollectUpload):
    collect_works = context['works_page'].paginator.object_list

    if any([c.upload_status_id != 1 for c in collect_works]):
        return

    union_works = []
    rel_maps = []

    for work_count, collect_work in enumerate(collect_works, start=1):
        work_id = collect_work.pk
        # Create work
        union_work = create_union_work(collect_work)
        union_work.save()
        union_works.append(union_work)

        # Link people
        people_maps = link_person_to_work(entities=context['authors'], relationship_type=REL_TYPE_CREATED,
                                          union_work=union_work, work_id=work_id, request=request)
        people_maps += link_person_to_work(entities=context['addressees'], relationship_type=REL_TYPE_WAS_ADDRESSED_TO,
                                           union_work=union_work, work_id=work_id, request=request)
        people_maps += link_person_to_work(entities=context['mentioned'],
                                           relationship_type=REL_TYPE_PEOPLE_MENTIONED_IN_WORK,
                                           union_work=union_work, work_id=work_id, request=request)
        rel_maps.append(people_maps)

        lang_maps = [CofkUnionLanguageOfWork(work=union_work, language_code=lang.language_code) for
                     lang in context['languages'].filter(iwork_id=work_id).all()]
        # Link languages
        rel_maps.append(lang_maps)

        # Link locations
        loc_maps = link_location_to_work(entities=context['destinations'], relationship_type=REL_TYPE_WAS_SENT_TO,
                                         union_work=union_work, work_id=work_id, request=request)
        loc_maps += link_location_to_work(entities=context['origins'], relationship_type=REL_TYPE_WAS_SENT_FROM,
                                          union_work=union_work, work_id=work_id, request=request)
        rel_maps.append(loc_maps)

        # Create manifestations
        union_maps = create_union_manifestations(work_id=work_id, union_work=union_work, request=request,
                                                 context=context)
        rel_maps.append(union_maps)

        res_maps = []

        # Link resources
        for resource in context['resources'].filter(iwork_id=work_id).all():
            union_resource = CofkUnionResource()
            union_resource.resource_url = resource.resource_url
            union_resource.resource_name = resource.resource_name
            union_resource.resource_details = resource.resource_details
            union_resource.resource_id = resource.resource_id
            union_resource.save()

            cwrm = CofkWorkResourceMap(relationship_type=REL_TYPE_IS_RELATED_TO, work=union_work,
                                       resource=union_resource, resource_id=union_resource.resource_id)
            cwrm.update_current_user_timestamp(request.user.username)
            # cwrm.save()
            res_maps.append(cwrm)

        rel_maps.append(res_maps)

        collect_work.upload_status_id = 4  # Accepted and saved into main database

    for rel_map in rel_maps:
        bulk_create(rel_map)

    CofkCollectWork.objects.bulk_update(collect_works, ['upload_status_id'])

    # Update values of related items
    qws = []

    for work in union_works:
        work.queryable.creators_for_display = work.creators_for_display
        work.queryable.places_from_for_display = work.places_from_for_display
        work.queryable.places_to_for_display = work.places_to_for_display
        work.queryable.addressees_for_display = work.addressees_for_display
        qws.append(work.queryable)

    CofkUnionQueryableWork.objects.bulk_update(qws, ['creators_for_display', 'places_from_for_display',
                                                     'places_to_for_display', 'addressees_for_display'])

    # Change state of upload and work
    upload.upload_status_id = 3  # Review complete
    upload.works_accepted = work_count
    upload.save()


def reject_works(context: dict, upload: CofkCollectUpload):
    collect_works = context['works_page'].paginator.object_list

    if any([c.upload_status_id != 1 for c in collect_works]):
        return

    for work_count, collect_work in enumerate(collect_works, start=1):
        collect_work.upload_status_id = 5  # Rejected

    CofkCollectWork.objects.bulk_update(collect_works, ['upload_status_id'])

    upload.upload_status_id = 3  # Review complete
    upload.works_rejected = work_count
    upload.save()
