from django.test import TestCase
from django.utils import timezone

from uploader.entities.entity import CofkEntity
from uploader.models import CofkCollectUpload, CofkCollectStatus


class MockEntity:
    def __init__(self, name):
        self.name = name

class TestValidation(TestCase):

    @classmethod
    def setUpTestData(cls):
        CofkCollectStatus().save()

    def setUp(self) -> None:
        self.new_upload = CofkCollectUpload()
        self.new_upload.upload_status_id = 1
        self.new_upload.uploader_email = 'test@user.com'
        self.new_upload.upload_timestamp = timezone.now()
        self.new_upload.save()

    def test_year(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))

        work.check_data_types({'date_of_work2_std_year': 's1945'})
        msg = 'Column date_of_work2_std_year in Work sheet is not a valid integer.'
        self.assertEqual(work.errors[1][0].message, msg)

    def test_year_limit(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))

        work.check_data_types({'date_of_work2_std_year': '1945'})
        msg = 'date_of_work2_std_year: is 1945 but must be between 1500 and 1900'
        self.assertEqual(work.errors[1][0].message, msg)

    def test_bool(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))
        work.check_data_types({'date_of_work_std_is_range': '1945'})

        msg = 'Column date_of_work_std_is_range in Work sheet is not a boolean value of either 0 or 1.'
        self.assertEqual(work.errors[1][0].message, msg)

    def test_bool_success(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))
        work.check_data_types({'date_of_work_std_is_range': 1})

        msg = 'Column date_of_work_std_year not present but needed when date of work is a range.'
        self.assertEqual(work.errors[1][0].message, msg)

    def test_ids(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))
        work.check_data_types({'author_ids': '1;2;s', 'author_names': 'a;b'})

        msg = 'Column author_ids in Work sheet contains a non-valid value.'
        msg_2 = 'Column author_names has fewer names than there are ids in author_ids.'
        self.assertEqual(work.errors[1][0].message, msg)
        self.assertEqual(work.errors[1][1].message, msg_2)

    def test_ids_success(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))
        work.check_data_types({'author_ids': '1;2;3', 'author_names': 'a;b;c'})

        self.assertEqual(work.errors, {})

    def test_name_too_long(self):
        work = CofkEntity(self.new_upload, MockEntity('People'))
        work.check_data_types({'primary_name': '1' * 201})

        msg = 'A value in the field primary_name is longer than the limit of 200 characters.'
        self.assertEqual(work.errors[1][0].message, msg)

    def test_date_field(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))
        work.check_data_types({'date_of_work2_std_day': 41,})

        msg = 'date_of_work2_std_day: is 41 but can not be greater than 31'
        self.assertEqual(work.errors[1][0].message, msg)

    def test_date_range(self):
        work = CofkEntity(self.new_upload, MockEntity('Work'))
        work.check_data_types({'date_of_work_std_year' : 1601, 'date_of_work_std_month': 4, 'date_of_work_std_day': 1,
                               'date_of_work2_std_year': 1600, 'date_of_work2_std_month': 4, 'date_of_work2_std_day': 1,
                               'date_of_work_std_is_range': 1,})

        msg = 'Column date_of_work_std_year can not be greater than date_of_work2_std_year.'
        self.assertEqual(work.errors[1][0].message, msg)
