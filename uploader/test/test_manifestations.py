import logging

from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedTestCase, spreadsheet_data

log = logging.getLogger(__name__)


class TestManifestations(UploadIncludedTestCase):

    def test_valid_manifestation_type(self):
        """
        A manifestation_type value that exists in the lookup map should produce no error.
        """
        data = {**spreadsheet_data, 'Manifestation': [
            [1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
        ]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertNotIn('manifestations', cuef.errors)

    def test_invalid_manifestation_type(self):
        """
        A manifestation_type value that does not exist in the lookup map should produce an error.
        """
        data = {**spreadsheet_data, 'Manifestation': [
            [1, 1, "XXX", 1, "Bodleian", "test", "test", '', '', '', '', ''],
        ]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('manifestations', cuef.errors)
        self.assertIn('XXX', cuef.errors['manifestations']['errors'][0]['errors'][0])

    def test_valid_manifestation_type_p(self):
        """
        A manifestation_type_p value that exists in the lookup map should produce no error
        after being remapped to manifestation_type.
        """
        data = {**spreadsheet_data, 'Manifestation': [
            [1, 1, '', '', '', '', '', "P", "test", "test", '', ''],
        ]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertNotIn('manifestations', cuef.errors)

    def test_invalid_manifestation_type_p(self):
        """
        A manifestation_type_p value that does not exist in the lookup map should produce an error,
        since it is remapped to manifestation_type before validation.
        """
        data = {**spreadsheet_data, 'Manifestation': [
            [1, 1, '', '', '', '', '', "INVALID", "test", "test", '', ''],
        ]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('manifestations', cuef.errors)
        self.assertIn('INVALID', cuef.errors['manifestations']['errors'][0]['errors'][0])
