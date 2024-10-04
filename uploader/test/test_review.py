import logging
import re

from django.core.exceptions import PermissionDenied

from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedFactoryTestCase, spreadsheet_data, upload_status, MockMessages
from uploader.views import upload_review

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

        request = self.factory.post("/upload", {'work_id': 'all', 'action': 'accept', 'confirm': ''})
        request.user = self.admin
        request._messages = MockMessages()

        response = upload_review(request, self.new_upload.upload_id)

        assert response.status_code == 302

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
