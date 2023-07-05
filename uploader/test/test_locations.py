import logging

from uploader.models import CofkCollectDestinationOfWork
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_utils import UploadIncludedTestCase

log = logging.getLogger(__name__)

class TestLocations(UploadIncludedTestCase):
    def test_extra_location_no_union(self):
        """
        This test provides two locations, Burford, which exists in the Union catalogue and
        Carisbrooke with an id that does not exist in the union database.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton", "15257", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 5,
             "test", 1, 1, "test", "", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             2, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 2],
                       ["newton", 15257],
                       ["Wren", 22859] ,],
            'Places': [['Burford', 400285],
                       ['Carisbrooke', 5]],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('There is no location with the id 5 in the Union catalogue.',
                     cuef.errors['locations']['errors'][0]['errors'])

    def test_extra_location(self):
        """
        This test provides two locations Burford and a new location, Cape town.
        This should not raise an error.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton", "15257", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Cape Town", '',
             "test", 1, 1, "test", "", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             885, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 885],
                       ["newton", 15257],
                       ["Wren", 22859],],
            'Places': [['Burford', 400285],
                       ['Cape Town']],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        # This is a valid upload and should be without errors
        self.assertEqual(cuef.errors, {})
        destinations = CofkCollectDestinationOfWork.objects.all()
        self.assertEqual(len(destinations), 1)
        self.assertEqual(destinations[0].location.location_name, 'Cape Town')