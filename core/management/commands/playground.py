import datetime
import datetime
import io
import logging
import re

from django.conf import settings
from django.core.management import BaseCommand

from core.helper import email_utils, model_utils, view_utils, django_utils, recref_utils
from location.models import CofkUnionLocation, CofkLocationCommentMap
import csv

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'playground for try some python code'

    def handle(self, *args, **options):
        main12()


def main12():
    records = """
cofk_union_comment,cofk_union_location,refers_to
cofk_union_comment,cofk_union_manifestation,refers_to
cofk_union_comment,cofk_union_manifestation,refers_to_date
cofk_union_comment,cofk_union_manifestation,refers_to_receipt_date
cofk_union_comment,cofk_union_person,refers_to
cofk_union_comment,cofk_union_work,refers_to
cofk_union_comment,cofk_union_work,refers_to_addressee
cofk_union_comment,cofk_union_work,refers_to_author
cofk_union_comment,cofk_union_work,refers_to_date
cofk_union_comment,cofk_union_work,refers_to_destination
cofk_union_comment,cofk_union_work,refers_to_origin
cofk_union_comment,cofk_union_work,refers_to_people_mentioned_in_work
cofk_union_comment,cofk_union_work,route
cofk_union_image,cofk_union_manifestation,image_of
cofk_union_image,cofk_union_person,image_of
cofk_union_institution,cofk_union_resource,is_related_to
cofk_union_location,cofk_union_resource,is_related_to
cofk_union_manifestation,cofk_union_institution,stored_in
cofk_union_manifestation,cofk_union_manifestation,enclosed_in
cofk_union_manifestation,cofk_union_work,is_manifestation_of
cofk_union_person,cofk_union_location,died_at_location
cofk_union_person,cofk_union_location,was_born_in_location
cofk_union_person,cofk_union_location,was_in_location
cofk_union_person,cofk_union_manifestation,formerly_owned
cofk_union_person,cofk_union_manifestation,handwrote
cofk_union_person,cofk_union_manifestation,partly_handwrote
cofk_union_person,cofk_union_person,acquaintance_of
cofk_union_person,cofk_union_person,collaborated_with
cofk_union_person,cofk_union_person,colleague_of
cofk_union_person,cofk_union_person,employed
cofk_union_person,cofk_union_person,friend_of
cofk_union_person,cofk_union_person,member_of
cofk_union_person,cofk_union_person,parent_of
cofk_union_person,cofk_union_person,relative_of
cofk_union_person,cofk_union_person,sibling_of
cofk_union_person,cofk_union_person,spouse_of
cofk_union_person,cofk_union_person,taught
cofk_union_person,cofk_union_person,unspecified_relationship_with
cofk_union_person,cofk_union_person,was_patron_of
cofk_union_person,cofk_union_resource,is_related_to
cofk_union_person,cofk_union_role_category,member_of
cofk_union_person,cofk_union_work,created
cofk_union_person,cofk_union_work,signed
cofk_union_work,cofk_union_location,mentions_place
cofk_union_work,cofk_union_location,was_sent_from
cofk_union_work,cofk_union_location,was_sent_to
cofk_union_work,cofk_union_person,intended_for
cofk_union_work,cofk_union_person,mentions
cofk_union_work,cofk_union_person,was_addressed_to
cofk_union_work,cofk_union_resource,is_related_to
cofk_union_work,cofk_union_subject,deals_with
cofk_union_work,cofk_union_work,is_reply_to
cofk_union_work,cofk_union_work,matches
cofk_union_work,cofk_union_work,mentions_work
    """

    def _to_class_name(text):
        text = re.sub(r'_(\w)', lambda i: i.group(1).upper(), text)
        text = text[0].upper() + text[1:]
        return text

    x = csv.reader(io.StringIO(records.strip()))
    print(x)
    cc = []
    for a, b, rel_type in x:
        a = _to_class_name(a)
        b = _to_class_name(b)
        print(f"('{rel_type}', {a}, {b}),")


def main11():
    print('hihihi')
    print(CofkLocationCommentMap.comment)
    print(type(CofkLocationCommentMap.comment))

    _models = recref_utils.find_all_recref_bounded_data()
    _models = list(_models)
    for c in _models:
        print(c)
    print(len(_models))


def main10():
    changed_field_choices = [
        ('', 'Date Of Birth Day'),
        ('', 'Date Of Birth Inferred'),
        ('', 'Date Of Birth Is Range'),
        ('', 'Date Of Birth Month'),
        ('', 'Date Of Birth Uncertain'),
        ('', 'Date Of Birth Year'),
        ('', 'Date Of Death'),
        ('', 'Date Of Death2 Day'),
        ('', 'Date Of Death2 Month'),
        ('', 'Date Of Death2 Year'),
        ('', 'Date Of Death Approx'),
        ('', 'Date Of Death Calendar'),
        ('', 'Date Of Death Day'),
        ('', 'Date Of Death Inferred'),
        ('', 'Date Of Death Is Range'),
        ('', 'Date Of Death Month'),
        ('', 'Date Of Death Uncertain'),
        ('', 'Date Of Death Year'),
        ('', 'Date Of Receipt As Marked'),
        ('', 'Date Of Work Approx'),
        ('', 'Date Of Work As Marked'),
        ('', 'Date of Work - Day (beginning of range or single date)'),
        ('', 'Date of Work - Day (end of range)'),
        ('', 'Date of Work (for ordering)'),
        ('', 'Date of Work (for ordering, Gregorian)'),
        ('', 'Date Of Work Inferred'),
        ('', 'Date of Work Is Range'),
        ('', 'Date of Work - Month (beginning of range or single date)'),
        ('', 'Date of Work - Month (end of range)'),
        ('', 'Date Of Work Uncertain'),
        ('', 'Date of Work - Year (beginning of range or single date)'),
        ('', 'Date of Work - Year (end of range)'),
        ('', 'Description'),
        ('', 'Destination As Marked'),
        ('', 'Destination Inferred'),
        ('', 'Destination Uncertain'),
        ('', 'Display Order'),
        ('', 'Editors Notes'),
        ('', 'Edit Status'),
        ('', 'Element 1 Eg Room'),
        ('', 'Element 2 Eg Building'),
        ('', 'Element 3 Eg Parish'),
        ('', 'Element 4 Eg City'),
        ('', 'Element 5 Eg County'),
        ('', 'Element 6 Eg Country'),
        ('', 'Element 7 Eg Empire'),
        ('', 'Endorsements'),
        ('', 'Excipit'),
        ('', 'Flourished'),
        ('', 'Flourished2 Day'),
        ('', 'Flourished2 Month'),
        ('', 'Flourished2 Year'),
        ('', 'Flourished Approx'),
        ('', 'Flourished Calendar'),
        ('', 'Flourished Day'),
        ('', 'Flourished Inferred'),
        ('', 'Flourished Is Range'),
        ('', 'Flourished Month'),
        ('', 'Flourished Uncertain'),
        ('', 'Flourished Year'),
        ('', 'Further Reading'),
        ('', 'Gender'),
        ('', 'Handling Instructions'),
        ('', 'ID number or shelfmark'),
        ('', 'Image Filename'),
        ('', 'Image Id'),
        ('', 'Images'),
        ('', 'Incipit'),
        ('', 'Institution City'),
        ('', 'Institution City Synonyms'),
        ('', 'Institution Country'),
        ('', 'Institution Country Synonyms'),
        ('', 'Institution Id'),
        ('', 'Institution Name'),
        ('', 'Institution Synonyms'),
        ('', 'Is Organisation'),
        ('', 'Keywords'),
        ('', 'Language Code'),
        ('', 'Language Of Manifestation'),
        ('', 'Language Of Work'),
        ('', 'Latitude'),
        ('', 'Licence Details'),
        ('', 'Licence Url'),
        ('', 'Location Id'),
        ('', 'Location Name'),
        ('', 'Location Synonyms'),
        ('', 'Longitude'),
        ('', 'Manifestation Creation Calendar'),
        ('', 'Manifestation Creation Date'),
        ('', 'Manifestation Creation Date2 Day'),
        ('', 'Manifestation Creation Date2 Month'),
        ('', 'Manifestation Creation Date2 Year'),
        ('', 'Manifestation Creation Date Approx'),
        ('', 'Manifestation Creation Date As Marked'),
        ('', 'Manifestation Creation Date Day'),
        ('', 'Manifestation Creation Date Gregorian'),
        ('', 'Manifestation Creation Date Inferred'),
        ('', 'Manifestation Creation Date Is Range'),
        ('', 'Manifestation Creation Date Month'),
        ('', 'Manifestation Creation Date Uncertain'),
        ('', 'Manifestation Creation Date Year'),
        ('', 'Manifestation Excipit'),
        ('', 'Manifestation Id'),
        ('', 'Manifestation Incipit'),
        ('', 'Manifestation Is Translation'),
        ('', 'Manifestation Ps'),
        ('', 'Manifestation Receipt Calendar'),
        ('', 'Manifestation Receipt Date'),
        ('', 'Manifestation Receipt Date2 Day'),
        ('', 'Manifestation Receipt Date2 Month'),
        ('', 'Manifestation Receipt Date2 Year'),
        ('', 'Manifestation Receipt Date Approx'),
        ('', 'Manifestation Receipt Date Day'),
        ('', 'Manifestation Receipt Date Gregorian'),
        ('', 'Manifestation Receipt Date Inferred'),
        ('', 'Manifestation Receipt Date Is Range'),
        ('', 'Manifestation Receipt Date Month'),
        ('', 'Manifestation Receipt Date Uncertain'),
        ('', 'Manifestation Receipt Date Year'),
        ('', 'Manifestation Type'),
        ('', 'Mentioned'),
        ('', 'Nationality Desc'),
        ('', 'Nationality Id'),
        ('', 'Non Delivery Reason'),
        ('', 'Non Letter Enclosures'),
        ('', 'Notes'),
        ('', 'Number Of Pages Of Document'),
        ('', 'Number Of Pages Of Text'),
        ('', 'Object Type'),
        ('', 'Opened'),
        ('', 'Organisation Type'),
        ('', 'Org Type Desc'),
        ('', 'Org Type Id'),
        ('', 'Original Calendar'),
        ('', 'Original Catalogue'),
        ('', 'Origin As Marked'),
        ('', 'Origin Inferred'),
        ('', 'Origin Uncertain'),
        ('', 'Other Details Summary'),
        ('', 'Other Details Summary Searchable'),
        ('', 'Other versions of name'),
        ('', 'Paper Size'),
        ('', 'Paper Type Or Watermark'),
        ('', 'Person Aliases'),
        ('', 'Person ID'),
        ('', 'Person ID (for internal system use)'),
        ('', 'Person or organisation name'),
        ('', 'Postage Costs'),
        ('', 'Postage Costs As Marked'),
        ('', 'Postage Marks'),
        ('', 'Printed Edition Details'),
        ('', 'Ps'),
        ('', 'Publication Details'),
        ('', 'Publication Id'),
        ('', 'Recd'),
        ('', 'Relevant To Cofk'),
        ('', 'Resource Details'),
        ('', 'Resource Id'),
        ('', 'Resource Name'),
        ('', 'Resource Url'),
        ('', 'Role Categories'),
        ('', 'Role Category Desc'),
        ('', 'Role Category Id'),
        ('', 'Routing Mark Ms'),
        ('', 'Routing Mark Stamp'),
        ('', 'Seal'),
        ('', 'Sent'),
        ('', 'Speed Entry Text'),
        ('', 'Speed Entry Text Id'),
        ('', 'Stored Folded'),
        ('', 'Subject Desc'),
        ('', 'Subject Id'),
        ('', 'Synonyms'),
        ('', 'Thumbnail'),
        ('', 'Uuid'),
        ('', 'Work ID'),
        ('', 'Work ID (for internal system use)'),
        ('', 'Work Is Translation'),
        ('', 'Work To Be Deleted'),
    ]

    db_names = [
        'date_of_birth_day',
        'date_of_birth_inferred',
        'date_of_birth_is_range',
        'date_of_birth_month',
        'date_of_birth_uncertain',
        'date_of_birth_year',
        'date_of_death',
        'date_of_death2_day',
        'date_of_death2_month',
        'date_of_death2_year',
        'date_of_death_approx',
        'date_of_death_calendar',
        'date_of_death_day',
        'date_of_death_inferred',
        'date_of_death_is_range',
        'date_of_death_month',
        'date_of_death_uncertain',
        'date_of_death_year',
        'date_of_work2_std_day',
        'date_of_work2_std_month',
        'date_of_work2_std_year',
        'date_of_work_approx',
        'date_of_work_as_marked',
        'date_of_work_inferred',
        'date_of_work_std',
        'date_of_work_std_day',
        'date_of_work_std_gregorian',
        'date_of_work_std_is_range',
        'date_of_work_std_month',
        'date_of_work_std_year',
        'date_of_work_uncertain',
        'desc_left_to_right',
        'desc_right_to_left',
        'description',
        'destination_as_marked',
        'destination_inferred',
        'destination_uncertain',
        'display_order',
        'editors_notes',
        'element_1_eg_room',
        'element_2_eg_building',
        'element_3_eg_parish',
        'element_4_eg_city',
        'element_5_eg_county',
        'element_6_eg_country',
        'element_7_eg_empire',
        'endorsements',
        'explicit',
        'flourished2_day',
        'flourished2_month',
        'flourished2_year',
        'flourished_calendar',
        'flourished_day',
        'flourished_is_range',
        'flourished_month',
        'flourished_year',
        'foaf_name',
        'further_reading',
        'id_number_or_shelfmark',
        'image_filename',
        'image_id',
        'incipit',
        'institution_city',
        'institution_city_synonyms',
        'institution_country',
        'institution_country_synonyms',
        'institution_id',
        'institution_name',
        'institution_synonyms',
        'iperson_id',
        'iwork_id',
        'keywords',
        'language_of_manifestation',
        'language_of_work',
        'latitude',
        'licence_details',
        'licence_url',
        'location_id',
        'location_name',
        'location_synonyms',
        'longitude',
        'manifestation_creation_calendar',
        'manifestation_creation_date',
        'manifestation_creation_date_approx',
        'manifestation_creation_date_day',
        'manifestation_creation_date_gregorian',
        'manifestation_creation_date_inferred',
        'manifestation_creation_date_month',
        'manifestation_creation_date_uncertain',
        'manifestation_creation_date_year',
        'manifestation_excipit',
        'manifestation_id',
        'manifestation_incipit',
        'manifestation_is_translation',
        'manifestation_type',
        'non_letter_enclosures',
        'number_of_pages_of_document',
        'number_of_pages_of_text',
        'organisation_type',
        'original_calendar',
        'origin_as_marked',
        'origin_inferred',
        'origin_uncertain',
        'paper_size',
        'paper_type_or_watermark',
        'person_aliases',
        'person_id',
        'postage_marks',
        'printed_edition_details',
        'ps',
        'publication_details',
        'publication_id',
        'relationship_code',
        'relationship_valid_from',
        'relationship_valid_till',
        'relevant_to_cofk',
        'resource_details',
        'resource_id',
        'resource_name',
        'resource_url',
        'seal',
        'skos_altlabel',
        'skos_hiddenlabel',
        'thumbnail',
        'work_id',
        'work_is_translation',
        'work_to_be_deleted',

    ]

    new_set = []
    for n in db_names:
        new_n = re.sub(r'(_\w)', lambda x: ' ' + x.group(1)[-1].upper(), n)
        new_n = new_n[0].upper() + new_n[1:]
        new_set.append((n, new_n))

    old_set = set(list(zip(*changed_field_choices))[1])
    a = []
    b = []
    for n in new_set:
        if n[1] in old_set:
            a.append(n)
        else:
            b.append(n[0])

    for aa in a:
        print(aa)

    for bb in b:
        print(bb)


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
    params = (
        '', None, None, datetime.datetime.now(), '', datetime.datetime.now(), '', None, None, '', '', '', '', '', '',
        '',
        None)
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
