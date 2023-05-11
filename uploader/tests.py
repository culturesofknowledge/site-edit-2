from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from uploader.models import CofkCollectUpload, CofkCollectStatus


class TestUpload(TestCase):

    def setUp(self) -> None:
        call_command('data_migration', **{'user': 'postgres', 'password': 'postgres',
                                          'host': 'db', 'database': 'ouls', 'model': CofkCollectStatus})

    def test_create_upload(self):
        new_upload = CofkCollectUpload()
        new_upload.upload_status_id = 1
        new_upload.uploader_email = 'test@user.com'
        new_upload.upload_timestamp = timezone.now()
        new_upload.save()

        self.assertEqual(new_upload.upload_status.status_desc, 'Awaiting review')
        self.assertEqual(new_upload.total_works, 0)
        self.assertEqual(new_upload.works_accepted, 0)
        self.assertEqual(new_upload.works_rejected, 0)
