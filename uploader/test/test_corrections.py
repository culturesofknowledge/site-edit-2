import logging
import tempfile

from openpyxl.workbook import Workbook

from core.models import CofkLookupCatalogue
from uploader.models import CofkCollectWorkCorrection
from uploader.review import accept_corrections, reject_corrections
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedFactoryTestCase
from uploader.validation import CofkExcelFileError
from work.models import CofkUnionWork

log = logging.getLogger(__name__)

CORRECTION_HEADERS = ['EMLO Letter ID Number', 'Command', 'Original Catalogue name']


class TestCorrectionUpload(UploadIncludedFactoryTestCase):

    def setUp(self):
        super().setUp()
        self.test_work = CofkUnionWork.objects.create(
            work_id='work_test_corrections_001',
            iwork_id=9901,
            creation_user='test',
            change_user='test',
        )
        self.test_work2 = CofkUnionWork.objects.create(
            work_id='work_test_corrections_002',
            iwork_id=9902,
            creation_user='test',
            change_user='test',
        )
        self.catalogue = CofkLookupCatalogue.objects.create(
            catalogue_code='TESTCAT',
            catalogue_name='Test Catalogue',
            is_in_union=0,
            publish_status=0,
        )
        self.tmp_files = []

    def tearDown(self):
        super().tearDown()

    def _make_file(self, header_row, data_rows, sheet_name='work'):
        wb = Workbook()
        ws = wb.create_sheet(sheet_name)
        ws.append(header_row)
        for row in data_rows:
            ws.append(row)
        tf = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        wb.save(tf.name)
        self.tmp_files.append(tf.name)
        return tf.name

    # --- Upload type detection ---

    def test_correction_upload_type_detected(self):
        """Lowercase 'work' sheet is detected as 'correction' upload type."""
        path = self._make_file(
            CORRECTION_HEADERS,
            [[9901, 'UPDATE', 'Test Catalogue']],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertEqual(cuef.upload_type, 'correction')

    def test_standard_work_sheet_not_confused_with_correction(self):
        """Uppercase 'Work' sheet is NOT treated as correction upload."""
        path = self._make_file(
            CORRECTION_HEADERS,
            [[9901, 'UPDATE', 'Test Catalogue']],
            sheet_name='Work',  # uppercase — standard upload
        )
        # Standard upload requires all 5 mandatory sheets; this will raise an error
        with self.assertRaises(CofkExcelFileError):
            CofkUploadExcelFile(self.new_upload, path)

    # --- Parsing: success cases ---

    def test_valid_row_creates_correction_record(self):
        """A valid data row creates a CofkCollectWorkCorrection with the correct corrections dict."""
        path = self._make_file(
            CORRECTION_HEADERS,
            [[9901, 'UPDATE', 'Test Catalogue']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        correction = CofkCollectWorkCorrection.objects.get(upload=self.new_upload, iwork_id=9901)
        self.assertEqual(correction.corrections, {'original_catalogue_code': 'TESTCAT'})
        self.assertEqual(correction.upload_status_id, 1)

    def test_union_work_fk_set_on_correction_record(self):
        """The union_work FK is populated when the iwork_id is found."""
        path = self._make_file(
            CORRECTION_HEADERS,
            [[9901, 'UPDATE', 'Test Catalogue']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        correction = CofkCollectWorkCorrection.objects.get(upload=self.new_upload, iwork_id=9901)
        self.assertEqual(correction.union_work_id, 9901)

    def test_multiple_correction_columns_stored(self):
        """All recognised correction columns in a row are included in the corrections dict."""
        headers = ['EMLO Letter ID Number', 'Command', 'Abstract', 'Keywords']
        path = self._make_file(
            headers,
            [[9901, 'UPDATE', 'A new abstract', 'keyword1; keyword2']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        correction = CofkCollectWorkCorrection.objects.get(upload=self.new_upload, iwork_id=9901)
        self.assertEqual(correction.corrections['abstract'], 'A new abstract')
        self.assertEqual(correction.corrections['keywords'], 'keyword1; keyword2')

    def test_multiple_rows_create_multiple_records(self):
        """Two valid rows produce two CofkCollectWorkCorrection objects."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Abstract'],
            [[9901, 'Abstract one'], [9902, 'Abstract two']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        self.assertEqual(
            CofkCollectWorkCorrection.objects.filter(upload=self.new_upload).count(), 2
        )

    def test_upload_total_works_set(self):
        """upload.total_works is set to the number of parsed corrections (in-memory, saved by handle_upload)."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Abstract'],
            [[9901, 'Abstract one'], [9902, 'Abstract two']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        self.assertEqual(self.new_upload.total_works, 2)

    # --- Parsing: catalogue FK lookup ---

    def test_valid_catalogue_lookup_stores_code(self):
        """'Original Catalogue name' is resolved to catalogue_code stored as original_catalogue_code."""
        path = self._make_file(
            CORRECTION_HEADERS,
            [[9901, 'UPDATE', 'Test Catalogue']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        correction = CofkCollectWorkCorrection.objects.get(upload=self.new_upload, iwork_id=9901)
        self.assertIn('original_catalogue_code', correction.corrections)
        self.assertEqual(correction.corrections['original_catalogue_code'], 'TESTCAT')
        self.assertNotIn('original_catalogue', correction.corrections)

    def test_unknown_catalogue_produces_error(self):
        """An unrecognised catalogue name produces a validation error."""
        path = self._make_file(
            CORRECTION_HEADERS,
            [[9901, 'UPDATE', 'NonExistentCatalogue']],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertGreater(cuef.total_errors, 0)
        self.assertEqual(CofkCollectWorkCorrection.objects.filter(upload=self.new_upload).count(), 0)

    # --- Parsing: validation errors ---

    def test_nonexistent_iwork_id_produces_error(self):
        """An iwork_id not in CofkUnionWork produces a validation error and no record."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Abstract'],
            [[99999, 'Some abstract']],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertGreater(cuef.total_errors, 0)
        self.assertEqual(CofkCollectWorkCorrection.objects.filter(upload=self.new_upload).count(), 0)

    def test_non_integer_identifier_produces_error(self):
        """A non-integer value in the identifier column produces a validation error."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Abstract'],
            [['notanumber', 'Some abstract']],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertGreater(cuef.total_errors, 0)

    def test_invalid_command_produces_error(self):
        """A Command value other than UPDATE produces a validation error."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Command', 'Abstract'],
            [[9901, 'DELETE', 'Some abstract']],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertGreater(cuef.total_errors, 0)

    def test_invalid_bool_field_produces_error(self):
        """A value of 2 for a boolean field produces a validation error."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Date inferred (0=No; 1=Yes)'],
            [[9901, 2]],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertGreater(cuef.total_errors, 0)

    def test_year_out_of_range_produces_error(self):
        """A year outside 1400-1900 produces a validation error."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Year date'],
            [[9901, 2025]],
        )
        cuef = CofkUploadExcelFile(self.new_upload, path)
        self.assertGreater(cuef.total_errors, 0)

    def test_row_with_no_correction_columns_skipped(self):
        """A row containing only the identifier (no correction fields) is skipped; upload fails with no valid rows."""
        path = self._make_file(
            ['EMLO Letter ID Number'],
            [[9901]],
        )
        with self.assertRaises(CofkExcelFileError):
            CofkUploadExcelFile(self.new_upload, path)
        self.assertEqual(CofkCollectWorkCorrection.objects.filter(upload=self.new_upload).count(), 0)

    def test_duplicate_iwork_id_only_first_kept(self):
        """Two rows with the same iwork_id result in only one CofkCollectWorkCorrection."""
        path = self._make_file(
            ['EMLO Letter ID Number', 'Abstract'],
            [[9901, 'First abstract'], [9901, 'Second abstract']],
        )
        CofkUploadExcelFile(self.new_upload, path)
        self.assertEqual(
            CofkCollectWorkCorrection.objects.filter(upload=self.new_upload, iwork_id=9901).count(), 1
        )
        correction = CofkCollectWorkCorrection.objects.get(upload=self.new_upload, iwork_id=9901)
        self.assertEqual(correction.corrections['abstract'], 'First abstract')

    def test_empty_sheet_raises_error(self):
        """A corrections sheet with no data rows raises CofkExcelFileError."""
        path = self._make_file(CORRECTION_HEADERS, [])
        with self.assertRaises(CofkExcelFileError):
            CofkUploadExcelFile(self.new_upload, path)

    # --- Accept/Reject ---

    def test_accept_corrections_applies_field_values(self):
        """accept_corrections() updates CofkUnionWork with the new field values."""
        CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=9901,
            union_work=self.test_work,
            corrections={'abstract': 'Corrected abstract'},
            upload_status_id=1,
        )
        accept_corrections(self.new_upload, username='testuser')
        self.test_work.refresh_from_db()
        self.assertEqual(self.test_work.abstract, 'Corrected abstract')

    def test_accept_corrections_sets_change_user(self):
        """accept_corrections() stamps the change_user on the updated work."""
        CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=9901,
            union_work=self.test_work,
            corrections={'abstract': 'Changed'},
            upload_status_id=1,
        )
        accept_corrections(self.new_upload, username='reviewer42')
        self.test_work.refresh_from_db()
        self.assertEqual(self.test_work.change_user, 'reviewer42')

    def test_accept_corrections_applies_catalogue_fk(self):
        """original_catalogue_code in corrections is correctly applied as original_catalogue_id."""
        CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=9901,
            union_work=self.test_work,
            corrections={'original_catalogue_code': 'TESTCAT'},
            upload_status_id=1,
        )
        accept_corrections(self.new_upload, username='testuser')
        self.test_work.refresh_from_db()
        self.assertEqual(self.test_work.original_catalogue_id, 'TESTCAT')

    def test_accept_corrections_sets_upload_status_accepted(self):
        """After accept_corrections(), upload.upload_status_id == 4."""
        CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=9901,
            union_work=self.test_work,
            corrections={'abstract': 'Changed'},
            upload_status_id=1,
        )
        accept_corrections(self.new_upload, username='testuser')
        self.new_upload.refresh_from_db()
        self.assertEqual(self.new_upload.upload_status_id, 4)

    def test_accept_corrections_sets_correction_status_accepted(self):
        """After accept_corrections(), each CofkCollectWorkCorrection.upload_status_id == 4."""
        correction = CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=9901,
            union_work=self.test_work,
            corrections={'abstract': 'Changed'},
            upload_status_id=1,
        )
        accept_corrections(self.new_upload, username='testuser')
        correction.refresh_from_db()
        self.assertEqual(correction.upload_status_id, 4)

    def test_reject_corrections_sets_status_rejected(self):
        """reject_corrections() sets correction records to status 5 and upload to status 3."""
        correction = CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=9901,
            union_work=self.test_work,
            corrections={'abstract': 'Changed'},
            upload_status_id=1,
        )
        reject_corrections(self.new_upload)
        correction.refresh_from_db()
        self.new_upload.refresh_from_db()
        self.assertEqual(correction.upload_status_id, 5)
        self.assertEqual(self.new_upload.upload_status_id, 3)

    def test_accept_corrections_does_not_modify_work_when_none(self):
        """accept_corrections() skips a correction whose union_work is None (work was deleted)."""
        CofkCollectWorkCorrection.objects.create(
            upload=self.new_upload,
            iwork_id=99999,
            union_work=None,
            corrections={'abstract': 'Changed'},
            upload_status_id=1,
        )
        # Should not raise; applied count will be 0
        accept_corrections(self.new_upload, username='testuser')
        self.new_upload.refresh_from_db()
        self.assertEqual(self.new_upload.upload_status_id, 4)
        self.assertEqual(self.new_upload.works_accepted, 0)
