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
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.db import connection as cur_conn
from django.db.models import Model, fields
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from psycopg2.extras import DictCursor

from audit.models import CofkUnionAuditLiteral, CofkUnionAuditRelationship
from core.helper import iter_utils, model_utils, recref_utils
from core.helper.model_utils import ModelLike
from core.models import CofkUnionResource, CofkUnionComment, CofkLookupDocumentType, CofkUnionRelationshipType, \
    CofkUnionImage, CofkUnionOrgType, CofkUnionRoleCategory, CofkUnionSubject, Iso639LanguageCode, CofkLookupCatalogue, \
    SEQ_NAME_ISO_LANGUAGE__LANGUAGE_ID
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from login.models import CofkUser
from manifestation.models import CofkUnionManifestation, CofkUnionLanguageOfManifestation
from person.models import CofkUnionPerson, SEQ_NAME_COFKUNIONPERSION__IPERSON_ID
from publication.models import CofkUnionPublication
from uploader.models import CofkCollectStatus, CofkCollectUpload, CofkCollectInstitution, CofkCollectLocation, \
    CofkCollectLocationResource, CofkCollectPerson, CofkCollectOccupationOfPerson, CofkCollectPersonResource, \
    CofkCollectInstitutionResource, CofkCollectWork, CofkCollectAddresseeOfWork, CofkCollectLanguageOfWork, \
    CofkCollectManifestation
from work import models as work_models
from work.models import CofkUnionWork, CofkUnionQueryableWork, CofkUnionLanguageOfWork

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
    start_sec = time.time()
    if check_duplicate_fn is None:
        def check_duplicate_fn(model):
            return model_class.objects.filter(pk=model.pk).exists()

    record_counter = iter_utils.RecordCounter()

    old_table_name = old_table_name or model_class._meta.db_table
    rows = find_rows_by_db_table(conn, old_table_name, batch_size=query_size)

    rows = map(dict, rows)
    if col_val_handler_fn_list:
        for _fn in col_val_handler_fn_list:
            rows = (_fn(r, conn) for r in rows)
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
        max_pk = model_utils.find_max_id(model_class, int_pk_col_name)
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


def log_save_records(target, size, used_sec):
    print(f'migrated records [{sec_to_min(used_sec):>7}][{size:>7,}][{target}]')


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


def _val_handler_users(row: dict, conn):
    row['password'] = row.pop('pw')
    row['is_active'] = row.pop('active')

    return row


def _val_handler_empty_str_null(row: dict, conn):
    for synonym in ['institution_synonyms', 'institution_city_synonyms', 'institution_country_synonyms',
                    'editors_notes', 'address', 'longitude', 'latitude']:
        if synonym in row and row[synonym] == '':
            del row[synonym]

    return row


def _val_handler_upload__upload_status(row: dict, conn):
    if row['upload_status']:
        row['upload_status'] = CofkCollectStatus.objects.get(pk=row['upload_status'])
    else:
        row['upload_status'] = None
    return row


def _val_handler_person__organisation_type(row: dict, conn):
    if row['organisation_type']:
        row['organisation_type'] = CofkUnionOrgType.objects.get(pk=row['organisation_type'])
    else:
        row['organisation_type'] = None

    return row


def migrate_groups_and_permissions(conn, target_model: str):
    rows = find_rows_by_db_table(conn, target_model)
    # All the entity types to which permissions are given
    content_types = [CofkUnionWork, CofkUnionPerson, CofkUnionLocation, CofkUnionComment,
                     CofkUnionResource, CofkUnionInstitution, CofkUnionManifestation, CofkUnionPublication]

    groups = {}

    for r in [dict(r) for r in rows]:
        g = Group.objects.get_or_create(name=r['role_code'])[0]
        groups[r['role_id']] = g

        for ct in content_types:
            content_type = ContentType.objects.get_for_model(ct)
            permissions = Permission.objects.filter(content_type=content_type)

            for p in permissions:
                if (g.name == 'reviewer' or g.name == 'cofkviewer') and p.codename.startswith('view_'):
                    g.permissions.add(p)
                elif g.name == 'cofkeditor' and (p.codename.startswith('view_') or p.codename.startswith('change_')):
                    g.permissions.add(p)
                elif g.name == 'super':
                    g.permissions.add(p)

    rows = find_rows_by_db_table(conn, 'cofk_user_roles')

    for r in rows:
        groups[r[1]].user_set.add(CofkUser.objects.get_by_natural_key(r[0]))


def _val_handler_work__catalogue(row: dict, conn):
    v = row.pop('original_catalogue')
    if v or v == '':
        row['original_catalogue_id'] = v
    else:
        row['original_catalogue_id'] = ''
    return row


def _val_handler_collect_person(row: dict, conn):
    if collect_person := CofkCollectPerson.objects.filter(iperson_id=row['iperson_id']).first():
        row['iperson_id'] = collect_person.pk

    return row


def _val_handler_language(row: dict, conn):
    if language := Iso639LanguageCode.objects.filter(code_639_3=row['language_code']).first():
        row['language_code'] = language

    return row


def _val_handler_collect_work(row: dict, conn):
    row['upload_status_id'] = row.pop('upload_status')

    return row


def _val_handler_collect_manifestation(row: dict, conn):
    if collect_work := CofkCollectWork.objects.filter(iwork_id=row['iwork_id']).first():
        row['iwork_id'] = collect_work.pk

    if collect_institution := CofkCollectInstitution.objects.filter(institution_id=row['repository_id']).first():
        row['repository_id'] = collect_institution.pk

    return row


def _val_handler_manif__work_id(row: dict, conn):
    sql = 'select right_id_value from cofk_union_relationship ' \
          f" where left_table_name = 'cofk_union_manifestation' " \
          f" and right_table_name = 'cofk_union_work' " \
          f" and left_id_value = %s "
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


def clone_recref_simple_by_field_pairs(
        conn, field_pairs: Iterable[tuple[ForwardManyToOneDescriptor, ForwardManyToOneDescriptor]]
):
    for field_a, field_b in field_pairs:
        clone_recref_simple(conn, field_a, field_b)
        clone_recref_simple(conn, field_b, field_a)


def create_check_fn_by_unique_together_model(model: Type[model_utils.ModelLike]):
    def _fn(instance: model_utils.ModelLike):
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


def data_migration(user, password, database, host, port):
    start_migrate = time.time()
    warnings.filterwarnings('ignore',
                            '.*DateTimeField .+ received a naive datetime .+ while time zone support is active.*')

    conn = psycopg2.connect(database=database, password=password,
                            user=user, host=host, port=port)
    print(conn)
    max_audit_literal_id = model_utils.find_max_id(CofkUnionAuditLiteral, 'audit_id') or 0
    max_audit_relationship_id = model_utils.find_max_id(CofkUnionAuditRelationship, 'audit_id') or 0

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

    # ### Uploads
    clone_rows_by_model_class(conn, CofkCollectUpload,
                              col_val_handler_fn_list=[_val_handler_upload__upload_status])

    # ### Publication
    clone_rows_by_model_class(conn, CofkUnionPublication)

    # ### Location
    clone_rows_by_model_class(conn, CofkUnionLocation)

    clone_rows_by_model_class(conn, CofkCollectLocation,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectLocation))
    clone_rows_by_model_class(conn, CofkCollectLocationResource,
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
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkCollectOccupationOfPerson))  # What uses this table?
    clone_rows_by_model_class(conn, CofkCollectPersonResource,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectPersonResource))

    # ### Repositories/institutions
    clone_rows_by_model_class(conn, CofkUnionInstitution,
                              col_val_handler_fn_list=[_val_handler_empty_str_null])

    clone_rows_by_model_class(conn, CofkCollectInstitution,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectInstitution))
    clone_rows_by_model_class(conn, CofkCollectInstitutionResource,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkCollectInstitutionResource))

    # ## Users

    clone_rows_by_model_class(conn, CofkUser,
                              col_val_handler_fn_list=[_val_handler_users],
                              seq_name=None,
                              old_table_name='cofk_users', )
    migrate_groups_and_permissions(conn, 'cofk_roles')

    # ### Work
    clone_rows_by_model_class(conn, CofkUnionWork,
                              col_val_handler_fn_list=[_val_handler_work__catalogue],
                              seq_name=work_models.SEQ_NAME_COFKUNIONWORK__IWORK_ID,
                              int_pk_col_name='iwork_id', )
    clone_rows_by_model_class(conn, CofkUnionQueryableWork, seq_name=None)
    clone_rows_by_model_class(conn, CofkUnionLanguageOfWork, col_val_handler_fn_list=[_val_handler_language],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkUnionLanguageOfWork))
    clone_rows_by_model_class(conn, CofkUnionLanguageOfManifestation, col_val_handler_fn_list=[_val_handler_language],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(
                                  CofkUnionLanguageOfManifestation))

    clone_rows_by_model_class(conn, CofkCollectWork,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectWork),
                              col_val_handler_fn_list=[_val_handler_collect_work],
                              )
    clone_rows_by_model_class(conn, CofkCollectAddresseeOfWork,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectAddresseeOfWork),
                              col_val_handler_fn_list=[_val_handler_collect_person])

    # clone_rows_by_model_class(conn, CofkCollectAuthorOfWork, check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectAuthorOfWork))
    # clone_rows_by_model_class(conn, CofkCollectDestinationOfWork, check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectDestinationOfWork))
    clone_rows_by_model_class(conn, CofkCollectLanguageOfWork, col_val_handler_fn_list=[_val_handler_language],
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectLanguageOfWork))
    # clone_rows_by_model_class(conn, CofkCollectOriginOfWork, check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectOriginOfWork))
    # clone_rows_by_model_class(conn, CofkCollectPersonMentionedInWork, check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectPersonMentionedInWork))
    # clone_rows_by_model_class(conn, CofkCollectSubjectOfWork, check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectSubjectOfWork))
    # clone_rows_by_model_class(conn, CofkCollectWorkResource, check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectWorkResource))

    # ### manif
    clone_rows_by_model_class(conn, CofkUnionManifestation,
                              col_val_handler_fn_list=[_val_handler_manif__work_id],
                              seq_name=None)
    clone_rows_by_model_class(conn, CofkCollectManifestation,
                              check_duplicate_fn=create_check_fn_by_unique_together_model(CofkCollectManifestation),
                              col_val_handler_fn_list=[_val_handler_collect_manifestation])

    # clone recref records
    bounded_pairs = (b.pair for b in recref_utils.find_all_recref_bounded_data())
    clone_recref_simple_by_field_pairs(conn, bounded_pairs)

    # remove all audit records that created by data_migrations
    print('remove all audit records that created by data_migrations')
    CofkUnionAuditLiteral.objects.filter(audit_id__gt=max_audit_literal_id).delete()
    CofkUnionAuditRelationship.objects.filter(audit_id__gt=max_audit_relationship_id).delete()
    print('[END] remove all audit')

    conn.close()

    print(f'total sec: {sec_to_min(time.time() - start_migrate)}')
