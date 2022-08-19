import sys
from typing import Type

from django.core.management import BaseCommand
from django.db import connection
from django.db.models import Model

from core.models import CofkUnionResource
from location.models import CofkUnionLocation


class Command(BaseCommand):
    help = 'Remove all data in database'

    def handle(self, *args, **options):
        remove_all_records()


def sql_delete_all(db_table):
    return f'delete from {db_table}'


def sql_delete_all_by_model_class(model_class: Type[Model]):
    return sql_delete_all(model_class._meta.db_table)


def remove_all_records():
    if input('Are you sure to remove all records? [yes/NO] ') != 'yes':
        sys.exit(1)

    cursor = connection.cursor()
    sql_list = [
        sql_delete_all('cofk_union_location_comments'),
        sql_delete_all('cofk_union_location_images'),
        sql_delete_all('cofk_union_location_resources'),
        sql_delete_all_by_model_class(CofkUnionLocation),
        sql_delete_all_by_model_class(CofkUnionResource),
    ]
    for sql in sql_list:
        print(f'execute: {sql}')
        cursor.execute(sql)
