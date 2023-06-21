import logging
import re

from django.core.exceptions import PermissionDenied

from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_utils import UploadIncludedFactoryTestCase
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

        data = {'Work': [[1,"test","J",1660,1,1,1660,1,2,1,1,1,1,"test","newton",15257,"test",1,1,"test","Wren",
                           22859,"test",1,1,"test","Burford",400285,"test",1,1,"Carisbrooke",782,"test",1,1,"test",
                           "test","fra;eng",'','','','','','',"test","test","test","Baskerville",885,"test",
                           "test","EMLO","http://emlo.bodleian.ox.ac.uk/","Early Modern Letters Online test"]],
                'People': [["Baskerville", 885],
                           ["newton", 15257],
                           ["Wren", 22859]],
                'Places': [['Burford', 400285],
                           ['Carisbrooke', 782]],
                'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test",'','','','',''],
                                  [2, 1,'','','','','', "P", "test", "test",'','']],
                'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        response = upload_review(request, self.new_upload.upload_id)

        upload_status = re.compile(r'Status: (?P<status>[\w|\s]+?) \| Number of works uploaded: (?P<works>\d+?) \|' \
                        r' Accepted: (?P<accepted>\d+?) \| Rejected: (?P<rejected>\d+?)')

        match = re.search(upload_status, str(response.content))

        self.assertEquals(cuef.errors, {})
        self.assertEquals(match.group('status'), 'Awaiting review')
        self.assertEquals(match.group('works'), '1')
        self.assertEquals(match.group('accepted'), '0')
        self.assertEquals(match.group('rejected'), '0')
