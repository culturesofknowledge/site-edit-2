import os
import re
import tempfile
from typing import Dict, List

from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.utils import timezone
from openpyxl.workbook import Workbook

from core import constant
from core.helper import perm_serv
from core.models import Iso639LanguageCode
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from login.models import CofkUser
from person.models import CofkUnionPerson
from uploader.constants import MANDATORY_SHEETS
from uploader.models import CofkCollectStatus, CofkCollectUpload

spreadsheet_data = {'Work': [
    [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton", 15257, "test", 1, 1, "test", "Wren",
     22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782, "test", 1, 1, "test",
     '', "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville", 885, "test",
     "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
    'People': [["Baskerville", 885],
               ["newton", 15257],
               ["Wren", 22859]],
    'Places': [['Burford', 400285],
               ['Carisbrooke', 782]],
    'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                      [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
    'Repositories': [['Bodleian', 1]]}

class MockMessages(object):
    """
    Messages middleware needs to be mocked because test factory bypasses middleware.
    """
    def add(self, *args):
        return None

    def __iter__(self):
        for each in self.__dict__.values():
            yield each



upload_status = re.compile(r'Status: (?P<status>[\w|\s]+?) \| Number of works uploaded: (?P<works>\d+?) \|' \
                r' Accepted: (?P<accepted>\d+?) \| Rejected: (?P<rejected>\d+?)')

class UploaderTestCase(TestCase):
    def create_excel_file(self, data: Dict[str, List[List]] = None) -> str:
        wb = Workbook()
        tf = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)

        for sheet_name in MANDATORY_SHEETS.keys():
            ws = wb.create_sheet(sheet_name)
            column_count = len(MANDATORY_SHEETS[sheet_name]['columns'])
            ws.append(MANDATORY_SHEETS[sheet_name]['columns'])
            ws.append(['-'] * column_count)

            if data and sheet_name in data:
                for row in data[sheet_name]:
                    ws.append(row)

        wb.save(tf.name)

        self.tmp_files.append(tf.name)

        return tf.name

    def setUp(self) -> None:
        self.tmp_files = []

    def tearDown(self) -> None:
        # Delete all tmp files
        for f in self.tmp_files:
            os.unlink(f)


class UploadIncludedTestCase(UploaderTestCase):
    def setUp(self) -> None:
        super().setUp()

        for i, s in enumerate(['Awaiting review', 'Partly reviewed', 'Review complete',
                               'Accepted and saved into main database', 'Rejected']):
            CofkCollectStatus.objects.create(status_id=i + 1, status_desc=s)


        for loc in [782, 400285]:
            CofkUnionLocation(pk=loc).save()

        for lang in ['eng', 'fra']:
            Iso639LanguageCode(code_639_3=lang).save()

        CofkUnionInstitution(institution_id=1,
                             institution_name='Bodleian',
                             institution_city='Oxford').save()

        for person in [{'person_id': 'a', 'iperson_id': 15257, 'foaf_name': 'Newton'},
                       {'person_id': 'b', 'iperson_id': 885, 'foaf_name': 'Baskerville'},
                       {'person_id': 'c', 'iperson_id': 22859, 'foaf_name': 'Wren'}]:
            CofkUnionPerson(**person).save()

        self.new_upload = CofkCollectUpload()
        self.new_upload.upload_status_id = 1
        self.new_upload.uploader_email = 'test@user.com'
        self.new_upload.upload_timestamp = timezone.now()
        self.new_upload.save()


class UploadIncludedFactoryTestCase(UploadIncludedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.user = CofkUser.objects.create(username='test')
        self.admin = CofkUser.objects.create(username='admin', is_staff=True)

        super_group = Group.objects.create(name='super')
        super_group.permissions.add(perm_serv.get_perm_by_full_name(constant.PM_CHANGE_COLLECTWORK))
        super_group.user_set.add(self.admin)
