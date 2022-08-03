import itertools
import warnings
from argparse import ArgumentParser
from typing import Type

import psycopg2
from django.core.management import BaseCommand
from django.db.models import Model
from psycopg2.extras import DictCursor

from location.models import CofkUnionLocation


def create_query_all_sql(db_table, schema='public'):
    return f'select * from {schema}.{db_table}'


def find_rows_by_db_table(conn, db_table):
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(create_query_all_sql(db_table))
    results = cursor.fetchall()
    return results


def clone_rows_by_model_class(conn, model_class: Type[Model], check_duplicate_fn=None):
    """ most simple method to copy rows from old DB to new DB
    * assume all column name are same
    * assume no column have been removed
    """
    if check_duplicate_fn is None:
        def check_duplicate_fn(model):
            return model_class.objects.filter(pk=model.pk).exists()

    rows = find_rows_by_db_table(conn, model_class._meta.db_table)
    rows = map(dict, rows)
    rows = (model_class(**r) for r in rows)
    rows = itertools.filterfalse(check_duplicate_fn, rows)
    rows = list(rows)
    print(f'save news records [{model_class}][{len(rows)}]')
    model_class.objects.bulk_create(rows, batch_size=500)


class Command(BaseCommand):
    help = 'Copy / move data from selected DB to project db '

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-u', '--user')
        parser.add_argument('-p', '--password')
        parser.add_argument('-d', '--database')
        parser.add_argument('-o', '--host')
        parser.add_argument('-t', '--port')

    def handle(self, *args, **options):
        data_migration(user=options['user'],
                       password=options['password'],
                       database=options['database'],
                       host=options['host'],
                       port=options['port'])


def data_migration(user, password, database, host, port):
    warnings.filterwarnings('ignore',
                            '.*DateTimeField .+ received a naive datetime .+ while time zone support is active.*')

    conn = psycopg2.connect(database=database, password=password,
                            user=user, host=host, port=port)
    print(conn)

    clone_action_fn_list = [
        lambda: clone_rows_by_model_class(conn, CofkUnionLocation)
    ]

    for fn in clone_action_fn_list:
        fn()

    conn.close()
