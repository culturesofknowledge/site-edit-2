import logging
from datetime import datetime
from typing import List, Type

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, models, transaction
from django.db.models import QuerySet
from django.urls import reverse

from cllib_django import email_utils
from core.constant import REL_TYPE_STORED_IN, REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, \
    REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_IS_RELATED_TO, \
    REL_TYPE_MENTION, REL_TYPE_DEALS_WITH, REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_COMMENT_DATE, \
    REL_TYPE_COMMENT_ORIGIN, REL_TYPE_COMMENT_DESTINATION, REL_TYPE_COMMENT_PERSON_MENTIONED, \
    REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_MENTION_PLACE
from core.models import CofkUnionResource, CofkLookupCatalogue, CofkUnionComment
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation import manif_serv
from manifestation.models import CofkUnionManifestation, CofkManifInstMap
from person.models import CofkUnionPerson, create_person_id
from uploader.models import CofkCollectUpload, CofkCollectWork, CofkCollectPerson, CofkCollectLocation
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkPersonMap, CofkWorkResourceMap, \
    CofkUnionLanguageOfWork, CofkWorkSubjectMap, CofkWorkCommentMap

log = logging.getLogger(__name__)


def create_union_work(union_work_dict: dict, collect_work: CofkCollectWork, username: str) -> CofkUnionWork:
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

    # EMLO Collect does not set the boolean date_of_work_std_is_range to true
    # if a second date is set. Therefore, we need to check if there are any values set
    # for the second date.
    # Note that this makes it a minimum requirement that the year be set for the second date.
    if not collect_work.date_of_work_std_is_range and collect_work.date_of_work2_std_year:
        union_work_dict['date_of_work_std_is_range'] = 1

    union_work = CofkUnionWork(**union_work_dict, init_seq_id=True)
    union_work.update_current_user_timestamp(username)

    return union_work


def link_person_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, username: str) \
        -> List[CofkWorkPersonMap]:
    person_maps = []
    for person in entities.select_related('iperson').all():
        cwpm = CofkWorkPersonMap(relationship_type=relationship_type,
                                 work=union_work, person=person.iperson.union_iperson,
                                 person_id=person.iperson.union_iperson.person_id)
        cwpm.update_current_user_timestamp(username)
        person_maps.append(cwpm)

    return person_maps


def link_location_to_work(entities: QuerySet, relationship_type: str, union_work: CofkUnionWork, username: str) \
        -> List[CofkWorkLocationMap]:
    location_maps = []
    for origin_or_dest in entities.select_related('location').all():
        cwlm = CofkWorkLocationMap(relationship_type=relationship_type,
                                   work=union_work, location=origin_or_dest.location.union_location,
                                   location_id=origin_or_dest.location.union_location.location_id)
        cwlm.update_current_user_timestamp(username)
        location_maps.append(cwlm)

    return location_maps

def link_comments_to_work(collect_work: CofkCollectWork, union_work: CofkUnionWork, username: str)\
        -> List[CofkWorkCommentMap]:
    comment_maps = []

    work_comment_map = [(collect_work.notes_on_date_of_work, REL_TYPE_COMMENT_DATE),
                        (collect_work.notes_on_authors, REL_TYPE_COMMENT_AUTHOR),
                        (collect_work.notes_on_addressees, REL_TYPE_COMMENT_ADDRESSEE),
                        (collect_work.notes_on_origin, REL_TYPE_COMMENT_ORIGIN),
                        (collect_work.notes_on_destination, REL_TYPE_COMMENT_DESTINATION),
                        (collect_work.notes_on_people_mentioned, REL_TYPE_COMMENT_PERSON_MENTIONED),
                        (collect_work.notes_on_letter, REL_TYPE_COMMENT_REFERS_TO)]

    for work_comment in work_comment_map:
        if work_comment[0]:
            union_comment = CofkUnionComment(comment=work_comment[0])
            union_comment.update_current_user_timestamp(username)
            union_comment.save()

            cwcm = CofkWorkCommentMap(comment=union_comment, work=union_work,
                                      relationship_type=work_comment[1])
            cwcm.update_current_user_timestamp(username)
            comment_maps.append(cwcm)

    return comment_maps


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


def get_collect_people(people: QuerySet, collect_people: List[CofkCollectPerson]) -> List[CofkCollectPerson]:
    return [p.iperson for p in people if p.iperson not in collect_people and p.iperson.union_iperson is None]


def get_collect_locations(locations: QuerySet, collect_locations: List[CofkCollectLocation]) -> List[CofkCollectLocation]:
    return [l.location for l in locations if l.location not in collect_locations and l.location.union_location is None]


def create_union_people_and_locations(collect_works, username: str):
    """
    This function iterates over related people and locations and creates new
    Union entities if they do not already exist.
    """
    collect_people = []
    collect_locations = []

    for collect_work in collect_works:
        collect_people.extend(get_collect_people(collect_work.people_mentioned.all(), collect_people))
        collect_people.extend(get_collect_people(collect_work.addressees.all(), collect_people))
        collect_people.extend(get_collect_people(collect_work.authors.all(), collect_people))

        collect_locations.extend(get_collect_locations(collect_work.destination.all(), collect_locations))
        collect_locations.extend(get_collect_locations(collect_work.origin.all(), collect_locations))
        collect_locations.extend(get_collect_locations(collect_work.places_mentioned.all(), collect_locations))

    for person in collect_people:
        union_iperson = CofkUnionPerson(foaf_name=person.primary_name)
        union_iperson.person_id = create_person_id(union_iperson.iperson_id)
        union_iperson.update_current_user_timestamp(username)
        union_iperson.save()
        person.union_iperson = union_iperson
        person.save()
        log.info(f'Created new union person {union_iperson}')

    for location in collect_locations:
        union_location = CofkUnionLocation(location_name=location.location_name)
        union_location.update_current_user_timestamp(username)
        union_location.save()
        location.union_location = union_location
        location.save()
        log.info(f'Created new union location {union_location}')


def accept_works(context: dict, upload: CofkCollectUpload, request=None, email_addresses: List[str] = None):
    filter_args = {'upload_status_id': 1}

    if 'work_id' in context and context['work_id'] != 'all':
        filter_args['iwork_id'] = context['work_id']

    collect_works = context['works_page'].paginator.object_list.filter(**filter_args)

    if not collect_works:
        msg = f'No works in the upload "{upload.upload_name}" can be accepted (was the page refreshed?).'
        if request:
            messages.error(request, msg)
        elif email_addresses:
            try:
                email_utils.send_email(email_addresses,
                                       subject='EMLO Works Accepted Result',
                                       content=msg)
            except Exception as e:
                log.error('Sending email failed')
                log.exception(e)
        return msg

    username = context['username']

    union_work_dict = {'accession_code': context['accession_code'] if 'accession_code' in context else None}

    if 'catalogue_code' in context and context['catalogue_code'] != '':
        union_work_dict['original_catalogue'] = CofkLookupCatalogue.objects \
            .filter(catalogue_code=context['catalogue_code']).first()

    try:
        # Wrap the creation of union objects inside a Django transaction to ensure
        # that if an exception is raised, the whole transaction is rolled back
        with transaction.atomic():
            create_works(collect_works, username, union_work_dict, upload, request)

    except Exception as e:
        log.error(f'Upload {upload} failed.')
        log.exception(e)


def create_works(collect_works, username, union_work_dict, upload, request):
    union_works = []
    union_manifs = []
    union_resources = []
    rel_maps = {}

    # Create new union people and locations at this stage to avoid
    # cache problems later
    create_union_people_and_locations(collect_works, username)

    for collect_work in collect_works:
        log.debug(f'Processing work: {collect_work}')
        # Create work
        union_work = create_union_work(union_work_dict, collect_work, username)
        union_works.append(union_work)

        # Link comments
        comment_maps = link_comments_to_work(collect_work=collect_work, union_work=union_work, username=username)
        add_rel_maps(rel_maps, comment_maps)

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
        loc_maps += link_location_to_work(entities=collect_work.places_mentioned,
                                          relationship_type=REL_TYPE_MENTION_PLACE,
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
            union_resource.update_current_user_timestamp(username)
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

        try:
            email_utils.send_email(upload.uploader_email,
                                   subject='EMLO Works Accepted Result',
                                   content=msg)
        except Exception as e:
            log.error('Sending email failed')
            log.exception(e)

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
