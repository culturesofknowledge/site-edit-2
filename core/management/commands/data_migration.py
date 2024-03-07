import itertools
import logging
import re
import time
import warnings
from argparse import ArgumentParser
from math import floor
from typing import Type, Callable, Iterable, Any

import django.db.utils
import psycopg2
import psycopg2.errors
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.db import connection as cur_conn
from django.db.models import Model, fields
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from psycopg2.extras import DictCursor

from audit.models import CofkUnionAuditLiteral, CofkUnionAuditRelationship
from cllib import iter_utils
from core import constant
from core.helper import model_serv, recref_serv, perm_serv
from core.helper.model_serv import ModelLike
from core.models import CofkUnionResource, CofkUnionComment, CofkLookupDocumentType, CofkUnionRelationshipType, \
    CofkUnionImage, CofkUnionOrgType, CofkUnionRoleCategory, CofkUnionSubject, Iso639LanguageCode, CofkLookupCatalogue, \
    SEQ_NAME_ISO_LANGUAGE__LANGUAGE_ID, CofkUserSavedQuery, CofkUserSavedQuerySelection, CofkUnionFavouriteLanguage
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from login.models import CofkUser
from manifestation.models import CofkUnionManifestation, CofkUnionLanguageOfManifestation, CofkManifManifMap
from person.models import CofkUnionPerson, SEQ_NAME_COFKUNIONPERSION__IPERSON_ID, CofkPersonPersonMap
from publication.models import CofkUnionPublication
from uploader.models import CofkCollectStatus, CofkCollectUpload, CofkCollectInstitution, CofkCollectLocation, \
    CofkCollectLocationResource, CofkCollectPerson, CofkCollectOccupationOfPerson, CofkCollectPersonResource, \
    CofkCollectInstitutionResource, CofkCollectWork, CofkCollectAddresseeOfWork, CofkCollectLanguageOfWork, \
    CofkCollectManifestation, CofkCollectAuthorOfWork, CofkCollectDestinationOfWork, CofkCollectOriginOfWork, \
    CofkCollectPersonMentionedInWork, CofkCollectSubjectOfWork, CofkCollectWorkResource, \
    CofkCollectPlaceMentionedInWork, CofkCollectImageOfManif
from work import models as work_models
from work.models import CofkUnionWork, CofkUnionLanguageOfWork, CofkWorkWorkMap

log = logging.getLogger(__name__)
default_schema = 'public'


def is_exists(conn, sql, vals=None):
    cursor = conn.cursor()
    cursor.execute(sql, vals)
    return cursor.fetchone() is not None


def create_query_all_sql(db_table, schema=default_schema):
    return f'select * from {schema}.{db_table}'


def create_seq_col_name(model_class: Type[Model]):
    return f'{model_class._meta.db_table}_{model_class._meta.pk.name}_seq'


def find_rows_by_db_table(conn, db_table, batch_size=100_000):
    return iter_records(conn, create_query_all_sql(db_table), cursor_factory=DictCursor, batch_size=batch_size)


def iter_records(conn, sql, cursor_factory=None, vals=None, batch_size=100_000):
    query_cursor = conn.cursor(cursor_factory=cursor_factory)
    query_cursor.execute(sql, vals)

    def _batch_records():
        while rows := query_cursor.fetchmany(batch_size):
            yield rows

    return itertools.chain.from_iterable(_batch_records())


def clone_rows_by_model_class(conn, model_class: Type[ModelLike],
                              check_duplicate_fn=None,
                              col_val_handler_fn_list: list[Callable[[dict, Any], dict]] = None,
                              seq_name: str | None = '',
                              int_pk_col_name='pk',
                              old_table_name=None,
                              query_size=100_000,
                              save_size=100_000):
    """ most simple method to copy rows from old DB to new DB
    * assume all column name are same
    * assume no column have been removed
    """

    def _update_row_by_col_val_handler_fn_list(_row):
        if not col_val_handler_fn_list:
            return _row
        for _fn in col_val_handler_fn_list:
            _row = _fn(_row, conn)
        return _row

    start_sec = time.time()
    if check_duplicate_fn is None:
        def check_duplicate_fn(model):
            return model_class.objects.filter(pk=model.pk).exists()

    record_counter = iter_utils.RecordCounter()

    old_table_name = old_table_name or model_class._meta.db_table
    rows = find_rows_by_db_table(conn, old_table_name, batch_size=query_size)

    rows = map(dict, rows)
    if col_val_handler_fn_list:
        rows = map(_update_row_by_col_val_handler_fn_list, rows)
    rows = (model_class(**r) for r in rows)
    rows = itertools.filterfalse(check_duplicate_fn, rows)
    rows = map(record_counter, rows)
    model_class.objects.bulk_create(rows, batch_size=save_size)
    log_save_records(f'{model_class.__module__}.{model_class.__name__}',
                     record_counter.cur_size(),
                     used_sec=time.time() - start_sec)

    if seq_name == '':
        seq_name = create_seq_col_name(model_class)

    if seq_name and int_pk_col_name:
        max_pk = model_serv.find_max_id(model_class, int_pk_col_name)
        if isinstance(max_pk, str):
            raise ValueError(f'max_pk should be int -- [{max_pk}][{type(max_pk)}]')

        new_val = 10_000_000
        if max_pk > new_val:
            new_val = max_pk + new_val

        cur_conn.cursor().execute(f"select setval('{seq_name}', {new_val})")


def sec_to_min(sec):
    sec = round(sec)
    if sec < 60:
        return f'{sec}s'
    return f'{floor(sec / 60)}m,{sec % 60}s'


def log_save_records(target, size, used_sec, text='migrated records'):
    print(f'{text} [{sec_to_min(used_sec):>7}][{size:>7,}][{target}]')


class Command(BaseCommand):
    help = 'Copy / move data from selected DB to project db '

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--password')
        parser.add_argument('-d', '--database')
        parser.add_argument('-o', '--host')
        parser.add_argument('-t', '--port')
        parser.add_argument('-a', '--include-audit', action='store_true', default=False)

    def handle(self, *args, **options):
        data_migration(user=options['user'],
                       password=options['password'],
                       database=options['database'],
                       host=options['host'],
                       port=options['port'], )


def create_common_relation_col_name(table_name):
    return table_name.replace('_', '') + '_id'


def insert_sql_val_list(sql_val_list: Iterable[tuple[str, Any]]) -> int:
    record_counter = iter_utils.RecordCounter()
    insert_cursor = cur_conn.cursor()
    for sql, vals in sql_val_list:
        # print(sql)
        # print(vals)
        try:
            insert_cursor.execute(sql, vals)
            record_counter.plus_one()
        except django.db.utils.IntegrityError as e:
            msg = str(e).replace('\n', ' ')
            if re.search(r'violates foreign key constraint.+Key .+is not present in table', msg, re.DOTALL):
                log.warning(msg)
            else:
                raise e
    return record_counter.cur_size()


def as_str_sql_val(val) -> str:
    if val is None:
        return 'null'
    return "'{}'".format(val)


class FieldVal:
    def fields(self) -> list[str]:
        return []

    def values(self, record: dict) -> list[Any]:
        return []


class RecrefIdFieldVal(FieldVal):
    def __init__(self,
                 cur_recref_class: Type[Model],
                 cur_left_field: ForwardManyToOneDescriptor,
                 cur_right_field: ForwardManyToOneDescriptor
                 ):
        self.cur_recref_class = cur_recref_class
        self.cur_left_field = cur_left_field
        self.cur_right_field = cur_right_field

    @property
    def mapping_table_name(self) -> str:
        return self.cur_recref_class._meta.db_table

    @property
    def cur_left_table_name(self) -> str:
        return self.cur_left_field.field.related_fields[0][1].model._meta.db_table

    @property
    def cur_right_table_name(self) -> str:
        return self.cur_right_field.field.related_fields[0][1].model._meta.db_table

    def prepare_val(self, field: ForwardManyToOneDescriptor, old_val):
        related_field = field.field.related_fields[0][1]
        if isinstance(related_field, fields.CharField):
            return old_val
        elif isinstance(related_field, (fields.IntegerField, fields.AutoField)):
            return int(old_val)
        else:
            raise NotImplementedError(f'unexpected field type {related_field}')

    def check_duplicate_fn(self, record: dict):
        cur_left_col_name, cur_right_col_name = self.fields()
        where_list = [
            f"{cur_left_col_name} = %s",
            f"{cur_right_col_name} = %s",
            "relationship_type = %s",
        ]
        sql = f'select 1 from {self.mapping_table_name} ' \
              f"where {' and '.join(where_list)} "
        vals = [
            *self.values(record),
            record['relationship_type'],
        ]
        return is_exists(cur_conn, sql, vals)

    def fields(self) -> list[str]:
        return [
            self.cur_left_field.field.related_fields[0][0].get_attname(),
            self.cur_right_field.field.related_fields[0][0].get_attname(),
        ]

    def values(self, record: dict) -> list[Any]:
        return [
            self.prepare_val(self.cur_left_field, record['left_id_value']),
            self.prepare_val(self.cur_right_field, record['right_id_value']),
        ]


class RecrefFieldVal(FieldVal):
    def fields(self) -> list[str]:
        return [
            'from_date',
            'to_date',
            'relationship_type',
            'creation_timestamp',
            'creation_user',
            'change_timestamp',
            'change_user',
        ]

    def values(self, record: dict) -> list[Any]:
        return [
            record['relationship_valid_from'],
            record['relationship_valid_till'],
            record['relationship_type'],
            record['creation_timestamp'],
            record['creation_user'],
            record['change_timestamp'],
            record['change_user'],
        ]


class CofkPersonPersonMapFieldVal(FieldVal):

    def fields(self) -> list[str]:
        return ['person_type']

    def values(self, record: dict) -> list[Any]:
        value_map = {
            'taught': 'teacher',
            'colleague_of': 'employer',
            'parent_of': 'parent',
            'relative_of': 'protege',
            'member_of': 'organisation',
            'friend_of': 'protege',
            'acquaintance_of': 'protege',
            'collaborated_with': 'employee',
            'employed': 'employee',
            'was_patron_of': 'patron',
            'spouse_of': 'patron',
            'unspecified_relationship_with': 'other',
            'sibling_of': 'other',
        }
        # KTODO double check mapping

        """
taught
unspecified_relationship_with
acquaintance_of
colleague_of
friend_of
parent_of
relative_of
member_of
collaborated_with
was_patron_of
spouse_of
sibling_of
employed
        """
        """
organisation
parent
children
employer
employee
teacher
student
patron
protege
other
        """

        return [
            value_map.get(record['relationship_type'], 'other'),
        ]


def create_sql_val_holder(vals) -> str:
    return ', '.join(['%s'] * len(vals))


def create_recref(conn,
                  id_field_val: RecrefIdFieldVal,
                  extra_field_val: FieldVal = None,
                  ):
    start_sec = time.time()
    extra_field_val = extra_field_val or FieldVal()

    sql = 'select * from cofk_union_relationship ' \
          f" where left_table_name = '{id_field_val.cur_left_table_name}' " \
          f" and right_table_name = '{id_field_val.cur_right_table_name}' "
    values = iter_records(conn, sql, cursor_factory=DictCursor)
    values = (r for r in values if not id_field_val.check_duplicate_fn(r))

    fields_sql = ', '.join(
        RecrefFieldVal().fields() + id_field_val.fields() + extra_field_val.fields()
    )
    sql_vals_list = (RecrefFieldVal().values(r) + id_field_val.values(r) + extra_field_val.values(r) for r in values)

    sql_val_list = (
        (
            (
                f'insert into {id_field_val.mapping_table_name} ({fields_sql}) '
                f"values ({create_sql_val_holder(sql_vals)})"
            ),
            sql_vals
        )
        for sql_vals in sql_vals_list
    )

    record_size = insert_sql_val_list(sql_val_list)
    log_save_records(id_field_val.mapping_table_name, record_size,
                     used_sec=time.time() - start_sec)


def no_duplicate_check(*args, **kwargs):
    return False


def _val_handler_users(row: dict, conn) -> dict:
    row['password'] = row.pop('pw')
    row['is_active'] = row.pop('active')

    return row


def _val_handler_empty_str_null(row: dict, conn) -> dict:
    for synonym in ['institution_synonyms', 'institution_city_synonyms', 'institution_country_synonyms',
                    'editors_notes', 'address', 'longitude', 'latitude']:
        if synonym in row and row[synonym] == '':
            del row[synonym]

    return row


def _val_handler_person__organisation_type(row: dict, conn) -> dict:
    row['organisation_type_id'] = row.pop('organisation_type')
    return row


def migrate_groups_and_permissions(conn):
    start_sec = time.time()

    group_permissions_dict = {
        # 'cofkviewer': [],
        # 'reviewer': [],
        'cofkeditor': [
            constant.PM_CHANGE_WORK,
            constant.PM_CHANGE_PERSON,
            constant.PM_CHANGE_PUBLICATION,
            constant.PM_CHANGE_LOCATION,
            constant.PM_CHANGE_INST,
            constant.PM_CHANGE_ROLECAT,
            constant.PM_CHANGE_LOOKUPCAT,
            constant.PM_CHANGE_SUBJECT,
            constant.PM_CHANGE_ORGTYPE,
            constant.PM_CHANGE_COLLECTWORK,
        ],
    }
    group_permissions_dict['super'] = group_permissions_dict['cofkeditor'] + [
        constant.PM_CHANGE_USER,
        constant.PM_CHANGE_COMMENT,
        constant.PM_VIEW_AUDIT,
        constant.PM_EXPORT_FILE_WORK,
        constant.PM_EXPORT_FILE_PERSON,
        constant.PM_EXPORT_FILE_LOCATION,
        constant.PM_EXPORT_FILE_INST,
    ]

    # fill group records
    old_id_groups = {}
    for r in find_rows_by_db_table(conn, 'cofk_roles'):
        old_id_groups[r['role_id']] = Group.objects.get_or_create(name=r['role_code'])[0]

    # add permissions to groups
    for group_name, permission_codes in group_permissions_dict.items():
        group = Group.objects.get(name=group_name)

        for permission_code in permission_codes:
            permission = perm_serv.get_perm_by_full_name(permission_code)
            if permission:
                group.permissions.add(permission)
            else:
                print(f'permission not found: {permission_code}')

    # add users to groups
    for r in find_rows_by_db_table(conn, 'cofk_user_roles'):
        old_id_groups[r['role_id']].user_set.add(CofkUser.objects.get_by_natural_key(r['username']))

    # is_staff
    CofkUser.objects.with_perm(constant.PM_CHANGE_USER).update(is_staff=True)

    log_save_records('group & permission', -1, time.time() - start_sec)


def _val_handler_work__catalogue(row: dict, conn) -> dict:
    v = row.pop('original_catalogue')
    if v or v == '':
        row['original_catalogue_id'] = v
    else:
        row['original_catalogue_id'] = ''
    return row


def _val_handler_work_drop_language_of_work(row: dict, conn) -> dict:
    if 'language_of_work' in row:
        del row['language_of_work']
    return row


def _correct_work(row: dict, upload_id) -> dict:
    iwork_id = row['iwork_id']

    fill_cofk_collect_ref_pk(row, CofkCollectWork, 'iwork_id')

    return row


def get_first_pk(query):
    return query.values_list('pk', flat=True).first()


def fill_cofk_collect_ref_pk(row, collect_class, ref_col_name):
    filter_kwargs = {
        ref_col_name: row[ref_col_name],
        'upload_id': row['upload_id']
    }

    if pk := get_first_pk(collect_class.objects.filter(**filter_kwargs)):
        row[ref_col_name] = pk
    else:
        log.warning('{} not found for upload: {}, {}: {}'.format(
            collect_class.__name__, row['upload_id'], ref_col_name, row[ref_col_name]
        ))


def _val_handler_collect_person(row: dict, conn) -> dict:
    upload_id = row['upload_id']

    if 'iwork_id' in row:
        row = _correct_work(row, upload_id)
    fill_cofk_collect_ref_pk(row, CofkCollectPerson, 'iperson_id')

    return row


def _val_handler_collect_location(row: dict, conn) -> dict:
    upload_id = row['upload_id']

    if 'iwork_id' in row:
        row = _correct_work(row, upload_id)

    fill_cofk_collect_ref_pk(row, CofkCollectLocation, 'location_id')

    return row


def _val_handler_collect_work(row: dict, conn) -> dict:
    upload_id = row['upload_id']
    row = _correct_work(row, upload_id)

    return row


def _val_handler_language(row: dict, conn):
    row['language_code_id'] = row.pop('language_code')
    return row


def _val_handler_collect_upload(row: dict, conn) -> dict:
    row['upload_status_id'] = row.pop('upload_status')
    return row


def _val_handler_user(row: dict, conn) -> dict:
    row['username_id'] = row.pop('username')
    return row


def _val_handler_collect_institution(row: dict, conn) -> dict:
    upload_id = row['upload_id']
    if pk := get_first_pk(CofkCollectInstitution.objects.filter(institution_id=row['institution_id'],
                                                                upload_id=upload_id)):
        row['institution_id'] = pk
    return row


def _val_handler_collect_manifestation(row: dict, conn) -> dict:
    upload_id = row['upload_id']

    row = _correct_work(row, upload_id)

    if pk := get_first_pk(CofkCollectInstitution.objects.filter(institution_id=row['repository_id'],
                                                                upload_id=upload_id)):
        row['repository_id'] = pk

    return row


def _val_handler_manif__work_id(row: dict, conn):
    sql = 'select right_id_value from cofk_union_relationship ' \
          " where left_table_name = 'cofk_union_manifestation' " \
          " and right_table_name = 'cofk_union_work' " \
          " and left_id_value = %s "
    vals = [row['manifestation_id']]
    results = list(iter_records(conn, sql, vals=vals))
    if len(results) == 1:
        row['work_id'] = results[0][0]
    elif len(results) > 1:
        log.warning(f'one manif should have one work relationship {vals} -- {results} ')
    return row


def clone_recref_simple(conn,
                        left_field: ForwardManyToOneDescriptor,
                        right_field: ForwardManyToOneDescriptor):
    if left_field.field.model != right_field.field.model:
        raise ValueError('assume left_field and right_field share in same model')

    return create_recref(
        conn,
        RecrefIdFieldVal(left_field.field.model, left_field, right_field),
    )


def choice_recref_clone_direction(field_a, field_b):
    """ only handle two fields in same model """

    def _choice_by_left_name(left_name):
        if field_a.field.name == left_name:
            return field_a, field_b
        else:
            return field_b, field_a

    recref_model = field_a.field.model

    mapping = [
        (CofkManifManifMap, CofkManifManifMap.manif_to.field.name),
        (CofkPersonPersonMap, CofkPersonPersonMap.person.field.name),
        (CofkWorkWorkMap, CofkWorkWorkMap.work_from.field.name),
    ]
    for cur_recref_model, left_name in mapping:
        if issubclass(recref_model, cur_recref_model):
            # KTODO double check CofkPersonPersonMap left right mapping correct, left should be person_id, right should be related_id
            return _choice_by_left_name(left_name)

    log.warning(f'unknown left right mapping {field_a.field.model}')
    return field_a, field_b


def clone_recref_simple_by_field_pairs(conn):
    bounded_pairs = (b.pair for b in recref_serv.find_all_recref_bounded_data())
    bounded_pairs: Iterable[tuple[ForwardManyToOneDescriptor, ForwardManyToOneDescriptor]]

    for field_a, field_b in bounded_pairs:
        if field_a.field.related_model == field_b.field.related_model:
            field_a, field_b = choice_recref_clone_direction(field_a, field_b)
            clone_recref_simple(conn, field_a, field_b)
        else:
            # clone both direction if two fields are in different models
            clone_recref_simple(conn, field_a, field_b)
            clone_recref_simple(conn, field_b, field_a)


def create_check_fn_by_unique_together_model(model: Type[model_serv.ModelLike]):
    def _fn(instance: model_serv.ModelLike):
        if not model._meta.unique_together:
            raise ValueError(f'{model} have no unique_together {model._meta.unique_together}')
        fields = [getattr(model, field_name) for field_name in model._meta.unique_together[0]]
        fields = [f.field for f in fields]
        lookup = {
            f.attname: f.value_from_object(instance)
            for f in fields
        }
        is_exist = fields[0].model.objects.filter(**lookup).exists()
        return is_exist

    return _fn


def create_destination_and_origin_records():
    start_sec = time.time()
    location_primary_map = {}
    origins = []
    destinations = []

    qs = CofkCollectWork.objects \
        .filter(origin_id__isnull=False) \
        .exclude(pk__in=list(CofkCollectOriginOfWork.objects.values_list('iwork_id', flat=True))).all()

    for w in qs:
        last_origin_id = CofkCollectOriginOfWork.objects.filter(upload_id=w.upload_id).values_list(
            'origin_id').order_by('-origin_id')

        if last_origin_id:
            next_origin_id = last_origin_id[0][0] + 1
        else:
            next_origin_id = 1

        if w.origin_id not in location_primary_map:
            origin_id = CofkCollectLocation.objects.filter(location_id=w.origin_id).values_list('pk').first()[0]
            location_primary_map[w.origin_id] = origin_id
        else:
            origin_id = location_primary_map[w.origin_id]

        origins.append(CofkCollectOriginOfWork(location_id=origin_id, iwork_id=w.pk,
                                               upload_id=w.upload_id,
                                               origin_id=next_origin_id))

    CofkCollectOriginOfWork.objects.bulk_create(origins)

    log_save_records(f'{CofkCollectOriginOfWork.__module__}.CofkCollectOriginOfWork', len(origins),
                     time.time() - start_sec, ' created records')
    start_sec = time.time()

    qs = CofkCollectWork.objects \
        .filter(destination_id__isnull=False) \
        .exclude(pk__in=list(CofkCollectDestinationOfWork.objects.values_list('iwork_id', flat=True))).all()

    for w in qs:
        last_destination_id = CofkCollectDestinationOfWork.objects.filter(upload_id=w.upload_id).values_list(
            'destination_id').order_by('-destination_id')

        if last_destination_id:
            next_destination_id = last_destination_id[0][0] + 1
        else:
            next_destination_id = 1

        if w.destination_id not in location_primary_map:
            destination_id = \
                CofkCollectLocation.objects.filter(location_id=w.destination_id).values_list('pk').first()[0]
            location_primary_map[w.destination_id] = destination_id
        else:
            destination_id = location_primary_map[w.destination_id]

        destinations.append(CofkCollectDestinationOfWork(location_id=destination_id, iwork_id=w.pk,
                                                         upload_id=w.upload_id,
                                                         destination_id=next_destination_id))

    CofkCollectDestinationOfWork.objects.bulk_create(destinations)

    log_save_records(f'{CofkCollectDestinationOfWork.__module__}.CofkCollectDestinationOfWork', len(destinations),
                     time.time() - start_sec, ' created records')


def data_migration(user, password, database, host, port):
    start_migrate = time.time()
    warnings.filterwarnings('ignore',
                            '.*DateTimeField .+ received a naive datetime .+ while time zone support is active.*')

    # old db connection
    conn = psycopg2.connect(database=database, password=password,
                            user=user, host=host, port=port)
    print(conn)
    max_audit_literal_id = model_serv.find_max_id(CofkUnionAuditLiteral, 'audit_id') or 0
    max_audit_relationship_id = model_serv.find_max_id(CofkUnionAuditRelationship, 'audit_id') or 0

    clone_rows_by_model_class(conn, CofkLookupCatalogue)
    clone_rows_by_model_class(conn, CofkLookupDocumentType)
    clone_rows_by_model_class(conn, Iso639LanguageCode,
                              seq_name=SEQ_NAME_ISO_LANGUAGE__LANGUAGE_ID,
                              int_pk_col_name='language_id',
                              )
    clone_rows_by_model_class(conn, CofkCollectStatus)  # Static lookup table
    clone_rows_by_model_class(conn, CofkUnionOrgType)  # Static lookup table
    clone_rows_by_model_class(conn, CofkUnionResource)
    clone_rows_by_model_class(conn, CofkUnionComment)
    clone_rows_by_model_class(conn, CofkUnionImage)
    clone_rows_by_model_class(conn, CofkUnionSubject)
    clone_rows_by_model_class(conn, CofkUnionRoleCategory)
    clone_rows_by_model_class(conn, CofkUnionRelationshipType, seq_name=None)
    clone_rows_by_model_class(conn, CofkUnionFavouriteLanguage, seq_name=None,
                              col_val_handler_fn_list=[_val_handler_language])

    # ### Uploads
    clone_rows_by_model_class(conn, CofkCollectUpload,
                              col_val_handler_fn_list=[_val_handler_collect_upload])

    # ### Publication
    clone_rows_by_model_class(conn, CofkUnionPublication)

    # ### Location
    clone_rows_by_model_class(conn, CofkUnionLocation)

    clone_rows_by_model_class(conn, CofkCollectLocation,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectLocation))
    clone_rows_by_model_class(conn, CofkCollectLocationResource,
                              col_val_handler_fn_list=[_val_handler_collect_location],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectLocationResource))

    # ### Person
    clone_rows_by_model_class(
        conn, CofkUnionPerson,
        col_val_handler_fn_list=[_val_handler_person__organisation_type, ],
        seq_name=SEQ_NAME_COFKUNIONPERSION__IPERSON_ID,
        int_pk_col_name='iperson_id',
    )

    # clone_rows_by_model_class(conn, CofkUnionPersonSummary, seq_name=None)

    clone_rows_by_model_class(conn, CofkCollectPerson,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectPerson))
    clone_rows_by_model_class(conn, CofkCollectOccupationOfPerson,
                              col_val_handler_fn_list=[_val_handler_collect_person],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkCollectOccupationOfPerson))  # What uses this table?
    clone_rows_by_model_class(conn, CofkCollectPersonResource,
                              col_val_handler_fn_list=[_val_handler_collect_person],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectPersonResource))

    # ### Repositories/institutions
    clone_rows_by_model_class(conn, CofkUnionInstitution,
                              col_val_handler_fn_list=[_val_handler_empty_str_null])

    clone_rows_by_model_class(conn, CofkCollectInstitution,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectInstitution))
    clone_rows_by_model_class(conn, CofkCollectInstitutionResource,
                              col_val_handler_fn_list=[_val_handler_collect_institution],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkCollectInstitutionResource))

    # ## Users

    clone_rows_by_model_class(conn, CofkUser,
                              col_val_handler_fn_list=[_val_handler_users],
                              seq_name=None,
                              old_table_name='cofk_users', )
    migrate_groups_and_permissions(conn)

    # Queries must be run after user
    clone_rows_by_model_class(conn, CofkUserSavedQuery, seq_name='cofk_user_saved_query_query_id_seq',
                              col_val_handler_fn_list=[_val_handler_user])
    clone_rows_by_model_class(conn, CofkUserSavedQuerySelection)

    # ### Work
    clone_rows_by_model_class(conn, CofkUnionWork,
                              col_val_handler_fn_list=[_val_handler_work__catalogue,
                                                       _val_handler_work_drop_language_of_work,
                                                       ],
                              seq_name=work_models.SEQ_NAME_COFKUNIONWORK__IWORK_ID,
                              int_pk_col_name='iwork_id', )
    clone_rows_by_model_class(conn, CofkUnionLanguageOfWork, col_val_handler_fn_list=[_val_handler_language],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkUnionLanguageOfWork))

    clone_rows_by_model_class(conn, CofkCollectWork,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectWork),
                              col_val_handler_fn_list=[_val_handler_collect_upload],
                              )
    clone_rows_by_model_class(conn, CofkCollectAddresseeOfWork,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectAddresseeOfWork),
                              col_val_handler_fn_list=[_val_handler_collect_person])

    clone_rows_by_model_class(conn, CofkCollectAuthorOfWork, col_val_handler_fn_list=[_val_handler_collect_person],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectAuthorOfWork))
    clone_rows_by_model_class(conn, CofkCollectDestinationOfWork,
                              col_val_handler_fn_list=[_val_handler_collect_location],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectDestinationOfWork))
    clone_rows_by_model_class(conn, CofkCollectOriginOfWork, col_val_handler_fn_list=[_val_handler_collect_location],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectOriginOfWork))
    clone_rows_by_model_class(conn, CofkCollectLanguageOfWork,
                              col_val_handler_fn_list=[_val_handler_language, _val_handler_collect_work],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectLanguageOfWork))
    clone_rows_by_model_class(conn, CofkCollectPersonMentionedInWork,
                              col_val_handler_fn_list=[_val_handler_collect_person],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkCollectPersonMentionedInWork))
    clone_rows_by_model_class(conn, CofkCollectSubjectOfWork, col_val_handler_fn_list=[_val_handler_collect_work],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectSubjectOfWork))
    clone_rows_by_model_class(conn, CofkCollectWorkResource, col_val_handler_fn_list=[_val_handler_collect_work],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectWorkResource))
    clone_rows_by_model_class(conn, CofkCollectPlaceMentionedInWork,
                              col_val_handler_fn_list=[_val_handler_collect_location],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkCollectPlaceMentionedInWork))

    create_destination_and_origin_records()

    # ### manif
    clone_rows_by_model_class(conn, CofkUnionManifestation,
                              col_val_handler_fn_list=[_val_handler_manif__work_id],
                              seq_name=None)
    clone_rows_by_model_class(conn, CofkCollectManifestation,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectManifestation),
                              col_val_handler_fn_list=[_val_handler_collect_manifestation])
    clone_rows_by_model_class(conn, CofkUnionLanguageOfManifestation, col_val_handler_fn_list=[_val_handler_language],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkUnionLanguageOfManifestation))
    clone_rows_by_model_class(conn, CofkCollectImageOfManif)

    # clone recref records
    clone_recref_simple_by_field_pairs(conn)

    # remove all audit records created by data_migrations
    print('remove all audit records created by data_migrations')
    CofkUnionAuditLiteral.objects.filter(audit_id__gt=max_audit_literal_id).delete()
    CofkUnionAuditRelationship.objects.filter(audit_id__gt=max_audit_relationship_id).delete()
    print('[END] remove all audit')

    conn.close()

    print(f'total sec: {sec_to_min(time.time() - start_migrate)}')
