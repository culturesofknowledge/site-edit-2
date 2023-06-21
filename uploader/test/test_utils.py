import os
import tempfile
from typing import Dict, List

from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.utils import timezone
from openpyxl.workbook import Workbook

from core import constant
from core.helper import perm_utils
from core.models import Iso639LanguageCode
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from login.models import CofkUser
from person.models import CofkUnionPerson
from uploader.constants import MANDATORY_SHEETS
from uploader.models import CofkCollectStatus, CofkCollectUpload


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
        CofkCollectStatus.objects.create(status_id=1,
                                         status_desc='Awaiting review')

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
        super_group.permissions.add(perm_utils.get_perm_by_full_name(constant.PM_CHANGE_COLLECTWORK))
        super_group.user_set.add(self.admin)
