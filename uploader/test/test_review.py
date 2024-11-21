import logging
import re

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from core.constant import REL_TYPE_CREATED
from uploader.review import accept_works
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedFactoryTestCase, spreadsheet_data, upload_status, MockMessages
from uploader.uploader_serv import DisplayableCollectWork
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
