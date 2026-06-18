import logging
import tempfile

from openpyxl.workbook import Workbook

from uploader.models import CofkCollectLocation
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedTestCase

log = logging.getLogger(__name__)

# Verbose column headers that trigger bulk detection (no 'location_name' in row 1)
BULK_LOCATIONS_HEADERS = [
    'Name of City/town/village', 'Name of County', 'Name of Country',
    'Name of District of city', 'Name of Building', 'Name of Room', 'Name of Empire',
    'Synonyms/Alternative names', 'LATITUDE', 'LONGITUDE',
    'GENERAL NOTES ON PLACE', "EDITORS' NOTES AND QUERIES",
    'RELATED RESOURCE NAME', 'RELATED RESOURCE URL',
]


class TestBulkLocations(UploadIncludedTestCase):

    def create_bulk_locations_file(self, data_rows: list) -> str:
        wb = Workbook()
        ws = wb.create_sheet('Places')
        ws.append(BULK_LOCATIONS_HEADERS)
        ws.append(['-'] * len(BULK_LOCATIONS_HEADERS))
        for row in data_rows:
            ws.append(row)
        tf = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        wb.save(tf.name)
        self.tmp_files.append(tf.name)
        return tf.name

    def _row(self, city=None, county=None, country=None, parish=None, building=None,
             room=None, empire=None, synonyms=None, latitude=None, longitude=None,
             notes=None, editors_notes=None, resource_name=None, resource_url=None):
        return [city, county, country, parish, building, room, empire,
                synonyms, latitude, longitude, notes, editors_notes,
                resource_name, resource_url]

    def test_bulk_locations_creates_records(self):
        """Valid bulk locations upload creates a CofkCollectLocation record with correct fields."""
        row = self._row(city='London', country='England', synonyms='Londinium',
                        editors_notes='capital city')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        self.assertEqual(CofkCollectLocation.objects.count(), 1)
        loc = CofkCollectLocation.objects.first()
        self.assertEqual(loc.element_4_eg_city, 'London')
        self.assertEqual(loc.element_6_eg_country, 'England')
        self.assertEqual(loc.location_synonyms, 'Londinium')
        self.assertEqual(loc.editors_notes, 'capital city')

    def test_bulk_locations_name_from_city_and_country(self):
        """location_name is constructed by joining available place component fields."""
        row = self._row(city='Oxford', country='England')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        loc = CofkCollectLocation.objects.first()
        self.assertEqual(loc.location_name, 'Oxford, England')

    def test_bulk_locations_name_from_all_components(self):
        """location_name includes all provided component fields in order."""
        row = self._row(city='Southwark', county='Surrey', country='England',
                        parish='St George', building='The Bell Inn', room='Room 3',
                        empire='British Empire')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        loc = CofkCollectLocation.objects.first()
        # Order: city, county, country, parish, building, room, empire
        self.assertEqual(
            loc.location_name,
            'Southwark, Surrey, England, St George, The Bell Inn, Room 3, British Empire'
        )

    def test_bulk_locations_name_from_country_only(self):
        """A single component field is sufficient to create a location."""
        row = self._row(country='Scotland')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        loc = CofkCollectLocation.objects.first()
        self.assertEqual(loc.location_name, 'Scotland')

    def test_bulk_locations_empty_row_error(self):
        """A row with no place component fields generates a validation error and no record is created."""
        row = self._row(synonyms='some alias', editors_notes='note')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('locations', cuef.errors)
        self.assertEqual(CofkCollectLocation.objects.count(), 0)

    def test_bulk_locations_duplicate_skipped(self):
        """Two rows with the same constructed name result in only one record."""
        rows = [
            self._row(city='London', country='England'),
            self._row(city='London', country='England'),
        ]
        filename = self.create_bulk_locations_file(rows)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        self.assertEqual(CofkCollectLocation.objects.count(), 1)

    def test_bulk_locations_multiple_records(self):
        """Multiple rows create multiple CofkCollectLocation records."""
        rows = [
            self._row(city='London', country='England'),
            self._row(city='Oxford', country='England'),
            self._row(city='Cambridge', county='Cambridgeshire', country='England'),
        ]
        filename = self.create_bulk_locations_file(rows)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        self.assertEqual(CofkCollectLocation.objects.count(), 3)

    def test_bulk_locations_latlong_stored_as_string(self):
        """Latitude and longitude provided as floats are stored as strings."""
        row = self._row(city='London', latitude=51.5074, longitude=-0.1278)
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        loc = CofkCollectLocation.objects.first()
        self.assertIsInstance(loc.latitude, str)
        self.assertIsInstance(loc.longitude, str)

    def test_bulk_locations_notes_stored(self):
        """notes_on_place field is stored correctly."""
        row = self._row(city='Rome', country='Italy', notes='Ancient city')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        loc = CofkCollectLocation.objects.first()
        self.assertEqual(loc.notes_on_place, 'Ancient city')

    def test_bulk_locations_upload_type_detected(self):
        """A Places-only bulk spreadsheet is detected as upload_type 'location'."""
        filename = self.create_bulk_locations_file([self._row(city='London')])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.upload_type, 'location')

    def test_bulk_locations_element_fields_stored(self):
        """All individual place component fields are stored on the location record."""
        row = self._row(city='Southwark', county='Surrey', country='England',
                        parish='St Saviour', building='Winchester House',
                        room='Great Hall', empire='British Empire')
        filename = self.create_bulk_locations_file([row])

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertEqual(cuef.errors, {})
        loc = CofkCollectLocation.objects.first()
        self.assertEqual(loc.element_4_eg_city, 'Southwark')
        self.assertEqual(loc.element_5_eg_county, 'Surrey')
        self.assertEqual(loc.element_6_eg_country, 'England')
        self.assertEqual(loc.element_3_eg_parish, 'St Saviour')
        self.assertEqual(loc.element_2_eg_building, 'Winchester House')
        self.assertEqual(loc.element_1_eg_room, 'Great Hall')
        self.assertEqual(loc.element_7_eg_empire, 'British Empire')
