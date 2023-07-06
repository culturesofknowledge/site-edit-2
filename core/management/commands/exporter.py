"""
export data to csv for Emlo-frontend
"""
import logging
import re
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

import requests
from django.core.management import BaseCommand
from django.db.models import Count, Q
from django.utils.html import strip_tags

import person.views
from core import constant
from core.constant import REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO, REL_TYPE_MENTION
from core.helper import query_utils, recref_utils, thread_utils, date_utils, query_cache_utils, model_utils
from core.helper.view_components import HeaderValues, DownloadCsvHandler
from core.models import CofkUnionImage, CofkUnionComment, CofkUnionRelationshipType, \
    CofkUnionResource
from core.services import media_service
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation, create_sql_count_work_by_location
from manifestation.models import CofkUnionManifestation
from person import person_utils
from person.models import CofkUnionPerson
from work import work_utils
from work.models import CofkUnionWork
from work.work_utils import DisplayableWork

log = logging.getLogger(__name__)
cache_username_map = {}
cached_catalogue_status = {}


def to_datetime_str(dt) -> str:
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def to_datetime_ms_str(dt) -> str:
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def _send_request(url, timeout=120):
    is_alive = False
    try:
        requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }, timeout=timeout)
        is_alive = True
    except Exception as e:
        log.debug(f'{type(e)} -- {str(e)}')
    return url, is_alive


def check_urls(urls: Iterable[str], n_thread=100) -> dict[str, bool]:
    results = {}
    for i, (url, is_alive) in enumerate(thread_utils.yield_run_fn_results(_send_request, zip(urls), n_thread=n_thread)):
        results[url] = is_alive
    return results


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-o', '--output_dir', type=str, default='.')

    def handle(self, *args, **options):
        export_all(options['output_dir'])


def get_values_by_names(obj, names: list[str]) -> Iterable:
    for name in names:
        yield getattr(obj, name)


def obj_to_values_by_convert_map(obj, header_list, convert_map: dict) -> Iterable:
    for name in header_list:
        val_fn = convert_map.get(name, lambda o: getattr(o, name))
        yield val_fn(obj)


def always_published(*args, **kwargs):
    return 1


def is_published_work(w) -> int:
    return int(not work_utils.is_hidden_work(w, cached_catalogue_status=cached_catalogue_status))


def is_published_by_filter_work(obj, work_prefix) -> int:
    return int(obj.__class__.objects.filter(work_utils.q_hidden_works(prefix=work_prefix) &
                                            Q(pk=obj.pk)).count() == 0)


def to_csv_pk(obj):
    return f'{model_utils.get_table_name(obj)}-{obj.pk}'


class CommentFrontendCsv(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            'comment_id',
            'comment',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'uuid',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'comment_id': to_csv_pk,
                          'published': lambda o: is_published_by_filter_work(o, 'cofkworkcommentmap__work'),
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


class ImageFrontendCsv(HeaderValues):
    def __init__(self, objects_factory):
        self.cache_urls_alive = load_cache_urls_alive((r.image_filename for r in objects_factory()))

    def get_header_list(self) -> list[str]:
        return [
            'image_id',
            'image_filename',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'thumbnail',
            'display_order',
            'licence_details',
            'licence_url',
            'credits',
            'uuid',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'image_id': to_csv_pk,
                          'published': self._is_published,
                          'image_filename': lambda o: self._cut_img_url(o.image_filename),
                          'thumbnail': lambda o: self._cut_img_url(o.thumbnail),
                          'display_order': lambda o: f'{o.display_order:04d} {o.image_filename}',
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)

    def _cut_img_url(self, v):
        if not isinstance(v, str):
            return v
        return re.sub(r'^' + media_service.IMG_URL, '/', v)

    def _is_published(self, obj):
        check_list = [
            ('work', lambda: is_published_by_filter_work(obj, 'cofkmanifimagemap__manif__work')),
            ('url', lambda: is_url_for_published(obj.image_filename, self.cache_urls_alive)),
        ]
        for name, fn in check_list:
            if not fn():
                log.debug(f'not published reason[{name}] {obj}')
                return 0

        return 1


class InstFrontendCsv(HeaderValues):

    def __init__(self):
        self.inst_document_count = self.count_inst_work()

    def count_inst_work(self):
        q = work_utils.q_visible_works(prefix='cofkmanifinstmap__manif__work', check_hidden_date=False)
        q &= recref_utils.create_q_rel_type(constant.REL_TYPE_STORED_IN, prefix='cofkmanifinstmap')
        queryset = (CofkUnionInstitution.objects
                    .values('institution_id')
                    .annotate(count=Count('institution_id'))
                    .values_list('institution_id', 'count')
                    .filter(q)
                    )
        return dict(queryset)

    def get_header_list(self) -> list[str]:
        return [
            'institution_id',
            'institution_name',
            'institution_synonyms',
            'institution_city',
            'institution_city_synonyms',
            'institution_country',
            'institution_country_synonyms',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'uuid',
            'address',
            'latitude',
            'longitude',
            'document_count',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'institution_id': to_csv_pk,
                          'document_count': lambda o: self.inst_document_count.get(o.institution_id, 0),
                          'published': always_published,
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


class LocationFrontendCsv(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            'location_id',
            'location_name',
            'latitude',
            'longitude',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'location_synonyms',
            'element_1_eg_room',
            'element_2_eg_building',
            'element_3_eg_parish',
            'element_4_eg_city',
            'element_5_eg_county',
            'element_6_eg_country',
            'element_7_eg_empire',
            'uuid',
            'sent_count',
            'recd_count',
            'mentioned_count',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'location_id': to_csv_pk,
                          'published': always_published,
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


class ManifFrontendCsv(HeaderValues):
    def __init__(self):
        self.lookup_doc_desc_map = query_cache_utils.create_lookup_doc_desc_map()

    def get_header_list(self) -> list[str]:
        return [
            'manifestation_id',
            'manifestation_type',
            'id_number_or_shelfmark',
            'printed_edition_details',
            'paper_size',
            'paper_type_or_watermark',
            'number_of_pages_of_document',
            'number_of_pages_of_text',
            'seal',
            'postage_marks',
            'endorsements',
            'non_letter_enclosures',
            'manifestation_creation_calendar',
            'manifestation_creation_date',
            'manifestation_creation_date_gregorian',
            'manifestation_creation_date_year',
            'manifestation_creation_date_month',
            'manifestation_creation_date_day',
            'manifestation_creation_date_inferred',
            'manifestation_creation_date_uncertain',
            'manifestation_creation_date_approx',
            'manifestation_is_translation',
            'language_of_manifestation',
            'address',
            'manifestation_incipit',
            'manifestation_excipit',
            'manifestation_ps',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'manifestation_creation_date2_year',
            'manifestation_creation_date2_month',
            'manifestation_creation_date2_day',
            'manifestation_creation_date_is_range',
            'manifestation_creation_date_as_marked',
            'opened',
            'uuid',
            'routing_mark_stamp',
            'routing_mark_ms',
            'handling_instructions',
            'stored_folded',
            'postage_costs_as_marked',
            'postage_costs',
            'non_delivery_reason',
            'date_of_receipt_as_marked',
            'manifestation_receipt_calendar',
            'manifestation_receipt_date',
            'manifestation_receipt_date_gregorian',
            'manifestation_receipt_date_year',
            'manifestation_receipt_date_month',
            'manifestation_receipt_date_day',
            'manifestation_receipt_date_inferred',
            'manifestation_receipt_date_uncertain',
            'manifestation_receipt_date_approx',
            'manifestation_receipt_date2_year',
            'manifestation_receipt_date2_month',
            'manifestation_receipt_date2_day',
            'manifestation_receipt_date_is_range',
            'accompaniments',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'manifestation_id': to_csv_pk,
                          'manifestation_type': lambda o: self.lookup_doc_desc_map.get(
                              o.manifestation_type, o.manifestation_type),
                          'published': lambda o: is_published_work(o.work),
                          'manifestation_creation_calendar': lambda o: date_utils.decode_calendar(
                              o.manifestation_creation_calendar),
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


class PersonFrontendCsv(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            'person_id',
            'foaf_name',
            'skos_altlabel',
            'skos_hiddenlabel',
            'person_aliases',
            'date_of_birth_year',
            'date_of_birth_month',
            'date_of_birth_day',
            'date_of_birth',
            'date_of_birth_inferred',
            'date_of_birth_uncertain',
            'date_of_birth_approx',
            'date_of_death_year',
            'date_of_death_month',
            'date_of_death_day',
            'date_of_death',
            'date_of_death_inferred',
            'date_of_death_uncertain',
            'date_of_death_approx',
            'gender',
            'is_organisation',
            'iperson_id',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'further_reading',
            'date_of_birth_calendar',
            'date_of_birth_is_range',
            'date_of_birth2_year',
            'date_of_birth2_month',
            'date_of_birth2_day',
            'date_of_death_calendar',
            'date_of_death_is_range',
            'date_of_death2_year',
            'date_of_death2_month',
            'date_of_death2_day',
            'flourished',
            'flourished_calendar',
            'flourished_is_range',
            'flourished_year',
            'flourished_month',
            'flourished_day',
            'flourished2_year',
            'flourished2_month',
            'flourished2_day',
            'uuid',
            'flourished_inferred',
            'flourished_uncertain',
            'flourished_approx',
            'sent_count',
            'recd_count',
            'mentioned_count',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'person_id': to_csv_pk,
                          'foaf_name': lambda o: person_utils.decode_person(o),
                          'sent_count': lambda o: o.sent,
                          'recd_count': lambda o: o.recd,
                          'mentioned_count': lambda o: o.mentioned,
                          'published': always_published
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


def creation_change_user_settings() -> dict:
    default_user = 'Unknown User'
    return {
        'creation_user': lambda o: cache_username_map.get(o.creation_user, default_user),
        'change_user': lambda o: cache_username_map.get(o.change_user, default_user),
        'creation_timestamp': lambda o: to_datetime_ms_str(o.creation_timestamp),
        'change_timestamp': lambda o: to_datetime_ms_str(o.change_timestamp),
    }


class RelTypeFrontendCsv(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            'relationship_code',
            'desc_left_to_right',
            'desc_right_to_left',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'published': always_published,
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


def is_http_url(url: str) -> bool:
    return isinstance(url, str) and url.startswith('http')


def load_cache_urls_alive(urls: Iterable[str]) -> dict[str, bool]:
    log.info('Loading cache_urls_alive...')
    urls = filter(None, urls)
    urls = (u for u in urls if is_http_url(u))
    urls = set(urls)
    cache_urls_alive = check_urls(urls)
    return cache_urls_alive


def is_url_for_published(url: str, cache_urls: dict[str, bool]) -> int:
    if not url:
        return 1
    if is_http_url(url):
        return int(cache_urls.get(url, False))
    return media_service.is_img_exists_by_url(url)


class ResourceFrontendCsv(HeaderValues):
    def __init__(self, objects_factory):
        self.cache_urls_alive = load_cache_urls_alive((r.resource_url for r in objects_factory()))

    def get_header_list(self) -> list[str]:
        return [
            'resource_id',
            'resource_name',
            'resource_details',
            'resource_url',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'uuid',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'resource_id': to_csv_pk,
                          'published': self._get_published,
                          'resource_name': self._get_resource_name,
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)

    def _get_resource_name(self, obj):
        name = getattr(obj, 'resource_name', None)
        if name == 'Selden End card':
            return 'Bodleian card catalogue'
        return name

    def _get_published(self, obj):
        return is_url_for_published(obj.resource_url, self.cache_urls_alive)


class WorkFrontendCsv(HeaderValues):
    def __init__(self):
        self.catalogue_map = query_cache_utils.create_catalogue_name_map()

    def get_header_list(self) -> list[str]:
        return [
            'work_id',
            'description',
            'date_of_work_as_marked',
            'original_calendar',
            'date_of_work_std',
            'date_of_work_std_gregorian',
            'date_of_work_std_year',
            'date_of_work_std_month',
            'date_of_work_std_day',
            'date_of_work2_std_year',
            'date_of_work2_std_month',
            'date_of_work2_std_day',
            'date_of_work_std_is_range',
            'date_of_work_inferred',
            'date_of_work_uncertain',
            'date_of_work_approx',
            'authors_as_marked',
            'addressees_as_marked',
            'authors_inferred',
            'authors_uncertain',
            'addressees_inferred',
            'addressees_uncertain',
            'destination_as_marked',
            'origin_as_marked',
            'destination_inferred',
            'destination_uncertain',
            'origin_inferred',
            'origin_uncertain',
            'abstract',
            'keywords',
            'language_of_work',
            'work_is_translation',
            'incipit',
            'explicit',
            'ps',
            'original_catalogue',
            'accession_code',
            'work_to_be_deleted',
            'iwork_id',
            'editors_notes',
            'edit_status',
            'relevant_to_cofk',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
            'uuid',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        convert_map = {
                          'work_id': to_csv_pk,
                          'published': is_published_work,
                          'accession_code': self._get_accession_code,
                          'original_calendar': lambda o: date_utils.decode_calendar(o.original_calendar),
                          'date_of_work_std_gregorian': lambda o: re.sub(r'^10000-', '9999-',
                                                                         o.date_of_work_std_gregorian),
                          'original_catalogue': lambda o: self.catalogue_map.get(o.original_catalogue_id,
                                                                                 'No catalogue specified'),
                          'abstract': lambda o: strip_tags(o.abstract),
                      } | creation_change_user_settings()
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)

    def _get_accession_code(self, obj):
        accession_code = getattr(obj, 'accession_code', None)
        if isinstance(accession_code, str) and accession_code.startswith('Selden End EAD import'):
            return accession_code.replace('Selden End EAD import', 'Bodleian card catalogue bulk import')
        return accession_code


class RelationshipFrontendCsv(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            'relationship_id',
            'left_table_name',
            'left_id_value',
            'relationship_type',
            'right_table_name',
            'right_id_value',
            'relationship_valid_from',
            'relationship_valid_till',
            'published',
        ]

    def obj_to_values(self, obj) -> Iterable:
        if isinstance(obj, dict):
            return [obj.get(k) for k in self.get_header_list()]

        left_obj, right_obj = recref_utils.get_left_right_rel_obj(obj)
        convert_map = {
            'relationship_id': to_csv_pk,
            'left_table_name': lambda o: model_utils.get_table_name(left_obj),
            'left_id_value': lambda o: to_csv_pk(left_obj),
            'relationship_type': lambda o: f'cofk_union_relationship_type-{o.relationship_type}',
            'right_table_name': lambda o: model_utils.get_table_name(right_obj),
            'right_id_value': lambda o: to_csv_pk(right_obj),
            'relationship_valid_from': lambda o: to_datetime_str(o.from_date),
            'relationship_valid_till': lambda o: to_datetime_str(o.to_date),
            'published': always_published,
        }
        return obj_to_values_by_convert_map(obj, self.get_header_list(), convert_map)


def create_location_queryset():
    queryset = CofkUnionLocation.objects
    annotate = {
        'sent_count': create_sql_count_work_by_location([REL_TYPE_WAS_SENT_FROM]),
        'recd_count': create_sql_count_work_by_location([REL_TYPE_WAS_SENT_TO]),
        'mentioned_count': create_sql_count_work_by_location([REL_TYPE_MENTION]),
    }
    queryset = query_utils.update_queryset(queryset, CofkUnionLocation, None, annotate=annotate)
    return queryset


def preloaded_csv_settings(objects_factory, target_csv_type_factory, model_class):
    return (
        objects_factory,
        lambda: target_csv_type_factory(objects_factory),
        model_class,
    )


def find_all_recrefs():
    for recref_class in recref_utils.find_all_recref_class():
        for r in recref_class.objects.iterator():
            yield r

    for manif in CofkUnionManifestation.objects.iterator():
        manif: CofkUnionManifestation
        yield {
            'relationship_id': f'{manif.pk}-{manif.work.pk}',
            'left_table_name': model_utils.get_table_name(manif),
            'left_id_value': to_csv_pk(manif),
            'relationship_type': constant.REL_TYPE_IS_MANIF_OF,
            'right_table_name': model_utils.get_table_name(manif.work),
            'right_id_value': to_csv_pk(manif.work),
            'relationship_valid_from': '',
            'relationship_valid_till': '',
            'published': 1,
        }


def export_all(output_dir: str = '.'):
    start_time = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    global cache_username_map
    cache_username_map = query_cache_utils.create_username_map()
    global cached_catalogue_status
    cached_catalogue_status = query_cache_utils.create_catalogue_status_map()

    settings = [
        preloaded_csv_settings(
            lambda: CofkUnionResource.objects.iterator(),
            ResourceFrontendCsv, CofkUnionResource),
        (lambda: CofkUnionComment.objects.iterator(),
         CommentFrontendCsv, CofkUnionComment),
        (lambda: CofkUnionInstitution.objects.iterator(),
         InstFrontendCsv, CofkUnionInstitution),
        (lambda: create_location_queryset().iterator(),
         LocationFrontendCsv, CofkUnionLocation),
        (lambda: CofkUnionManifestation.objects.iterator(),
         ManifFrontendCsv, CofkUnionManifestation),
        (lambda: person.views.create_queryset_by_queries(CofkUnionPerson, ).iterator(),
         PersonFrontendCsv, CofkUnionPerson),
        (lambda: CofkUnionRelationshipType.objects.iterator(),
         RelTypeFrontendCsv, CofkUnionRelationshipType),
        (lambda: DisplayableWork.objects.iterator(),
         WorkFrontendCsv, CofkUnionWork),
        (find_all_recrefs, RelationshipFrontendCsv, 'cofk_union_relationship'),
        preloaded_csv_settings(
            lambda: CofkUnionImage.objects.iterator(),
            ImageFrontendCsv, CofkUnionImage),
    ]
    for objects_factory, target_csv_type_factory, name_item in settings:
        filename = name_item if isinstance(name_item, str) else name_item._meta.db_table
        csv_path = output_dir / f'{filename}.csv'
        log.info(f'exporting to {csv_path}')
        DownloadCsvHandler(target_csv_type_factory()).create_csv_file(
            objects_factory(),
            csv_path)

    log.info(f'exported all in {(time.time() - start_time) / 60:.2f} minutes')
