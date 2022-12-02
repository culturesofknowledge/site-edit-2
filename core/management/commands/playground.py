import datetime
import logging

from django.conf import settings
from django.core.management import BaseCommand

from core.helper import email_utils, model_utils, view_utils
from location.models import CofkUnionLocation

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'playground for try some python code'

    def handle(self, *args, **options):
        main9()

def main9():
    # sql = 'update "cofk_union_location" ("location_name") values (%s) '
    sql = 'UPDATE public.cofk_union_location SET location_name = %s WHERE location_id = %s'
    from django.db import connection as cur_conn

    cursor = cur_conn.cursor()
    cursor.execute(sql, ('a', 20000056,))
    cur_conn.commit()
    # cursor.commit()

    # r = cursor.fetchone()
    # print(r)

def main8():
    sql = 'INSERT INTO "cofk_union_location" ("location_name", "latitude", "longitude", "creation_timestamp", "creation_user", "change_timestamp", "change_user", "location_synonyms", "editors_notes", "element_1_eg_room", "element_2_eg_building", "element_3_eg_parish", "element_4_eg_city", "element_5_eg_county", "element_6_eg_country", "element_7_eg_empire", "uuid") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING "cofk_union_location"."location_id"'
    params = ('', None, None, datetime.datetime.now(), '', datetime.datetime.now(), '', None, None, '', '', '', '', '', '', '', None)
    from django.db import connection as cur_conn

    cursor = cur_conn.cursor()
    cursor.execute(sql, params)
    r = cursor.fetchone()
    print(cursor.rowcount)
    print(r)



def main7():
    loc = CofkUnionLocation()
    print('-----------------------------')
    print(loc.location_id)
    loc.save()
    loc.refresh_from_db()
    print(loc.location_id)
    print('-----------------------------')
    # f = pkg_resources.resource_stream('audit', 'trigger/dbf_cofk_union_audit_any.sql' )
    # print(f.read())
    # print('hihi')



def main6():
    # new_lang_formset = view_utils.create_formset(
    #     LangForm,
    #     prefix='new_lang',
    #     extra=0,
    #     # initial_list=model_utils.models_to_dict_list(comments_query_fn(rel_type))
    # )
    from core.forms import CommentForm
    comment_formset = view_utils.create_formset(CommentForm,
                                                prefix='loc_comment',
                                                initial_list=[], )
    breakpoint()
    print(comment_formset.is_valid())
    print(comment_formset.errors)
    # print(new_lang_formset.is_valid())
    # print(new_lang_formset.errors)

    print('xkxjkxjkxjk')


def main1():
    from core.models import CofkUnionResource
    # from location import fixtures
    from location.models import CofkUnionLocation
    print('yyyyyy')
    res: CofkUnionResource = CofkUnionResource(
        # resource_id = models.AutoField(primary_key=True)
        resource_name='resource_name val',
        resource_details='resource_details val',
        resource_url='resource_url val',
        # creation_timestamp = models.DateTimeField(blank=True, null=True)
        creation_user='creation_user val',
        # change_timestamp = models.DateTimeField(blank=True, null=True)
        change_user='change_user val',
        # uuid = models.UUIDField(blank=True, null=True)
    )
    res.save()

    loc: CofkUnionLocation = CofkUnionLocation.objects.first()
    l = list(loc.resources.iterator())
    print(l)
    loc.resources.add(l[0])
    # loc.resources.add(res)
    # loc.save()

    loc.refresh_from_db()

    print(list(loc.resources.iterator()))
    # x = loc.resources.a
    # print(x)

    # coll_location: CofkCollectLocation = CofkCollectLocation.objects.first()
    # a = coll_location.resources
    # print(coll_location)
    # print(a)


def main2():
    from location import fixtures
    loc_a = fixtures.create_location_a()
    print(loc_a.location_id)
    loc_a.save()
    print(loc_a.location_id)


def main3():
    from core.models import CofkUnionComment
    print(settings.MEDIA_ROOT)

    c = CofkUnionComment()
    c.update_current_user_timestamp('aaa')
    print(c.__dict__)


def main4():
    email_utils.send_email('errorzetabeta@gmail.com', 'testtingingi', 'yoooooooo')
    # You can see a record of this email in your logs: https://app.mailgun.com/app/logs.

    # You can send up to 300 emails/day from this sandbox server.
    # Next, you should add your own domain so you can send 10000 emails/month for free.


def main5():
    result = model_utils.next_seq_safe('xxkks')
    print(result)
