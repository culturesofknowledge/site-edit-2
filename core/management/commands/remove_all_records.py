import sys

from django.core.management import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Remove all data in database'

    def handle(self, *args, **options):
        remove_all_records()


def remove_all_records():
    if input('Are you sure to remove all records? [yes/NO] ') != 'yes':
        sys.exit(1)

    cursor = connection.cursor()
    sql_list = [
        'delete from cofk_union_location_comments',
        'delete from cofk_union_location_images',
        'delete from cofk_union_location_resources',
        'delete from cofk_union_location',
    ]
    for sql in sql_list:
        print(f'execute: {sql}')
        cursor.execute(sql)
