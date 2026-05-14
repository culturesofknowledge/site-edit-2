import logging
import re

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from core.constant import REL_TYPE_CREATED
from location.models import CofkUnionLocation
from person.models import CofkUnionPerson
from uploader.models import CofkCollectLocation, CofkCollectPerson
from uploader.review import accept_works, accept_locations, accept_people
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedFactoryTestCase, UploadIncludedTestCase, \
    spreadsheet_data, upload_status, MockMessages
from uploader.uploader_serv import DisplayableCollectWork
from uploader.views import upload_review
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


class TestAcceptLocations(UploadIncludedTestCase):

    def _make_collect_location(self, **kwargs):
        defaults = dict(
            upload=self.new_upload,
            location_id=1,
            location_name='London, England',
            element_1_eg_room='Room 3',
            element_2_eg_building='The Bell Inn',
            element_3_eg_parish='St George',
            element_4_eg_city='London',
            element_5_eg_county='Middlesex',
            element_6_eg_country='England',
            element_7_eg_empire='British Empire',
            location_synonyms='Londinium',
            editors_notes='capital city',
            latitude='51.5074',
            longitude='-0.1278',
        )
        defaults.update(kwargs)
        return CofkCollectLocation.objects.create(**defaults)

    def test_accept_locations_copies_all_fields(self):
        """accept_locations copies all fields from CofkCollectLocation to CofkUnionLocation."""
        self._make_collect_location()

        accept_locations(self.new_upload, username='admin')

        union_loc = CofkUnionLocation.objects.exclude(pk__in=[782, 400285]).get()
        self.assertEqual(union_loc.location_name, 'London, England')
        self.assertEqual(union_loc.element_1_eg_room, 'Room 3')
        self.assertEqual(union_loc.element_2_eg_building, 'The Bell Inn')
        self.assertEqual(union_loc.element_3_eg_parish, 'St George')
        self.assertEqual(union_loc.element_4_eg_city, 'London')
        self.assertEqual(union_loc.element_5_eg_county, 'Middlesex')
        self.assertEqual(union_loc.element_6_eg_country, 'England')
        self.assertEqual(union_loc.element_7_eg_empire, 'British Empire')
        self.assertEqual(union_loc.location_synonyms, 'Londinium')
        self.assertEqual(union_loc.editors_notes, 'capital city')
        self.assertEqual(union_loc.latitude, '51.5074')
        self.assertEqual(union_loc.longitude, '-0.1278')

    def test_accept_locations_links_collect_to_union(self):
        """accept_locations sets union_location FK on the collect record."""
        collect_loc = self._make_collect_location()

        accept_locations(self.new_upload, username='admin')

        collect_loc.refresh_from_db()
        self.assertIsNotNone(collect_loc.union_location)

    def test_accept_locations_name_only(self):
        """accept_locations works when only location_name is set (no element fields)."""
        CofkCollectLocation.objects.create(
            upload=self.new_upload, location_id=1, location_name='Rome',
        )

        accept_locations(self.new_upload, username='admin')

        union_loc = CofkUnionLocation.objects.exclude(pk__in=[782, 400285]).get()
        self.assertEqual(union_loc.location_name, 'Rome')


class TestAcceptPeople(UploadIncludedTestCase):

    def _make_collect_person(self, **kwargs):
        defaults = dict(
            upload=self.new_upload,
            iperson_id=9001,
            primary_name='Isaac Newton',
            gender='M',
            is_organisation='N',
            editors_notes='physicist',
            date_of_birth_year=1643,
            date_of_birth_month=1,
            date_of_birth_day=4,
            date_of_birth_inferred=1,
            date_of_birth_uncertain=0,
            date_of_birth_approx=0,
            date_of_birth_is_range=0,
            date_of_birth2_year=None,
            date_of_birth2_month=None,
            date_of_birth2_day=None,
            date_of_death_year=1727,
            date_of_death_month=3,
            date_of_death_day=31,
            date_of_death_inferred=0,
            date_of_death_uncertain=0,
            date_of_death_approx=0,
            date_of_death_is_range=0,
            date_of_death2_year=None,
            date_of_death2_month=None,
            date_of_death2_day=None,
        )
        defaults.update(kwargs)
        return CofkCollectPerson.objects.create(**defaults)

    def test_accept_people_copies_all_fields(self):
        """accept_people copies all fields from CofkCollectPerson to CofkUnionPerson."""
        self._make_collect_person()

        accept_people(self.new_upload, username='admin')

        union_person = CofkUnionPerson.objects.exclude(iperson_id__in=[15257, 885, 22859]).get()
        self.assertEqual(union_person.foaf_name, 'Isaac Newton')
        self.assertEqual(union_person.gender, 'M')
        self.assertEqual(union_person.is_organisation, 'N')
        self.assertEqual(union_person.editors_notes, 'physicist')
        self.assertEqual(union_person.date_of_birth_year, 1643)
        self.assertEqual(union_person.date_of_birth_month, 1)
        self.assertEqual(union_person.date_of_birth_day, 4)
        self.assertEqual(union_person.date_of_birth_inferred, 1)
        self.assertEqual(union_person.date_of_birth_uncertain, 0)
        self.assertEqual(union_person.date_of_birth_approx, 0)
        self.assertEqual(union_person.date_of_birth_is_range, 0)
        self.assertEqual(union_person.date_of_death_year, 1727)
        self.assertEqual(union_person.date_of_death_month, 3)
        self.assertEqual(union_person.date_of_death_day, 31)
        self.assertEqual(union_person.date_of_death_inferred, 0)
        self.assertEqual(union_person.date_of_death_uncertain, 0)
        self.assertEqual(union_person.date_of_death_approx, 0)
        self.assertEqual(union_person.date_of_death_is_range, 0)

    def test_accept_people_links_collect_to_union(self):
        """accept_people sets union_iperson FK on the collect record."""
        collect_person = self._make_collect_person()

        accept_people(self.new_upload, username='admin')

        collect_person.refresh_from_db()
        self.assertIsNotNone(collect_person.union_iperson)

    def test_accept_people_name_only(self):
        """accept_people works when only primary_name is set."""
        CofkCollectPerson.objects.create(
            upload=self.new_upload, iperson_id=9001,
            primary_name='John Doe', gender='', is_organisation='',
        )

        accept_people(self.new_upload, username='admin')

        union_person = CofkUnionPerson.objects.exclude(iperson_id__in=[15257, 885, 22859]).get()
        self.assertEqual(union_person.foaf_name, 'John Doe')


class TestReview(UploadIncludedFactoryTestCase):

    def test_permission(self):
        # Create an instance of a GET request.
        request = self.factory.get("/upload")
        request.user = self.user

        self.assertRaises(PermissionDenied, upload_review, request, self.new_upload.upload_id)

    def test_admin_permission(self):
        # Create an instance of a GET request.
        request = self.factory.get("/upload")
        request.user = self.admin

        filename = self.create_excel_file(spreadsheet_data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        response = upload_review(request, self.new_upload.upload_id)

        match = re.search(upload_status, str(response.content))

        self.assertEqual(cuef.errors, {})
        self.assertEqual(match.group('status'), 'Awaiting review')
        self.assertEqual(match.group('works'), '1')
        self.assertEqual(match.group('accepted'), '0')
        self.assertEqual(match.group('rejected'), '0')

    def test_accept_upload(self):
        filename = self.create_excel_file(spreadsheet_data)
        prefetch = ['authors', 'addressees', 'people_mentioned', 'languages', 'subjects', 'manifestations', 'resources',
                    'upload_status', 'addressees__iperson', 'authors__iperson', 'people_mentioned__iperson',
                    'manifestations__repository', 'authors__iperson__union_iperson',
                    'addressees__iperson__union_iperson', 'origin__location', 'destination__location',
                    'origin__location__union_location', 'destination__location__union_location',
                    'languages__language_code']
        cuef = CofkUploadExcelFile(self.new_upload, filename)

        works_paginator = Paginator(DisplayableCollectWork.objects.filter(upload=self.new_upload)
                                    .prefetch_related(*prefetch).order_by('pk'), 1000)

        context = { 'work_id': 'all', 'works_page': works_paginator.get_page(1), 'username': self.admin.username }

        accept_works(context, self.new_upload)
        name_of_first_author = next(CofkUnionWork.objects.first().find_persons_by_rel_type(REL_TYPE_CREATED)).foaf_name

        self.assertEqual(cuef.errors, {})
        self.assertEqual(self.new_upload.upload_status.status_id, 3)
        self.assertEqual(self.new_upload.total_works, 1)
        self.assertEqual(self.new_upload.works_accepted, 1)
        self.assertEqual(self.new_upload.works_rejected, 0)
        self.assertEqual(name_of_first_author, 'Newton')

    def test_reject_upload(self):
        filename = self.create_excel_file(spreadsheet_data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        request = self.factory.post("/upload", {'work_id': 'all', 'action': 'reject', 'confirm': ''})
        request.user = self.admin
        request._messages = MockMessages()

        response = upload_review(request, self.new_upload.upload_id)

        match = re.search(upload_status, str(response.content))

        self.assertEqual(cuef.errors, {})
        self.assertEqual(match.group('status'), 'Review complete')
        self.assertEqual(match.group('works'), '1')
        self.assertEqual(match.group('accepted'), '0')
        self.assertEqual(match.group('rejected'), '1')
