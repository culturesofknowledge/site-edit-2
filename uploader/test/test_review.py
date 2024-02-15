import logging
import re

from django.core.exceptions import PermissionDenied

from core.constant import REL_TYPE_CREATED
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedFactoryTestCase, spreadsheet_data, upload_status, MockMessages
from uploader.views import upload_review
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


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

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        request = self.factory.post("/upload", {'confirm_accept': ''})
        request.user = self.admin
        request._messages = MockMessages()

        response = upload_review(request, self.new_upload.upload_id)

        match = re.search(upload_status, str(response.content))

        self.assertEqual(cuef.errors, {})
        self.assertEqual(match.group('status'), 'Review complete')
        self.assertEqual(match.group('works'), '1')
        self.assertEqual(match.group('accepted'), '1')
        self.assertEqual(match.group('rejected'), '0')

        self.assertEqual(next(CofkUnionWork.objects.all()[0].find_persons_by_rel_type(REL_TYPE_CREATED)).foaf_name,
                          'Newton')

    def test_reject_upload(self):
        filename = self.create_excel_file(spreadsheet_data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        request = self.factory.post("/upload", {'reject_work': ''})
        request.user = self.admin
        request._messages = MockMessages()

        response = upload_review(request, self.new_upload.upload_id)

        match = re.search(upload_status, str(response.content))

        self.assertEqual(cuef.errors, {})
        self.assertEqual(match.group('status'), 'Review complete')
        self.assertEqual(match.group('works'), '1')
        self.assertEqual(match.group('accepted'), '0')
        self.assertEqual(match.group('rejected'), '1')
