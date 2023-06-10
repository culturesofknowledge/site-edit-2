from django.core.exceptions import PermissionDenied

from uploader.test.test_utils import UploadIncludedFactoryTestCase
from uploader.views import upload_review


class TestReview(UploadIncludedFactoryTestCase):


    def test_permission(self):
        # Create an instance of a GET request.
        request = self.factory.get("/upload")
        request.user = self.user

        self.assertRaises(PermissionDenied, upload_review, request)