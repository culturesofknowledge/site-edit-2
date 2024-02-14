import logging

from uploader.models import CofkCollectAuthorOfWork
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_serv import UploadIncludedTestCase

log = logging.getLogger(__name__)


class TestPeople(UploadIncludedTestCase):

    def test_extra_person_no_union(self):
        """
        This test provides two people, Baskerville with an id that does not exist in the union
        database.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton", "15257", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             2, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 2],
                       ["newton", 15257],
                       ["Wren", 22859], ],
            'Places': [['Burford', 400285],
                       ['Carisbrooke', 782]],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('There is no person with the id 2 in the Union catalogue.',
                      cuef.errors['people']['errors'][0]['errors'])

    def test_extra_person_omit_author_id_semicolon(self):
        """
        This test provides two author names listed, newton;Someone but only one id, 15257, and no
        semi-colon for the id. This should raise an error.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton;Someone", "15257", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             885, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 885],
                       ["newton", 15257],
                       ["Wren", 22859],
                       ["Someone"]],
            'Places': [['Burford', 400285],
                       ['Carisbrooke', 782]],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('Column author_ids has fewer ids than there are names in author_names.',
                      cuef.errors['work']['errors'][0]['errors'])

    def test_extra_person_non_valid_id(self):
        """
        This test provides two author names listed, newton;Someone and two ids, 15257 and 'x'.
        This should raise an error.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton;Someone", "15257;x", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             885, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 885],
                       ["newton", 15257],
                       ["Wren", 22859],
                       ["Someone", "x"]],
            'Places': [['Burford', 400285],
                       ['Carisbrooke', 782]],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('Column author_ids in Work sheet contains a non-valid value.',
                      cuef.errors['work']['errors'][0]['errors'])
        self.assertIn('Column iperson_id in People sheet contains a non-valid value.',
                      cuef.errors['people']['errors'][0]['errors'])

    def test_extra_person(self):
        """
        This test provides two author names listed, newton;Someone and one id, 15257 but containing a semi-colon for
        the ids to indicate a new person should be created.
        This should not raise an error.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton;Someone", "15257;", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             885, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 885],
                       ["newton", 15257],
                       ["Wren", 22859],
                       ["Someone"]],
            'Places': [['Burford', 400285],
                       ['Carisbrooke', 782]],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        # This is a valid upload and should be without errors
        self.assertEqual(cuef.errors, {})
        authors = CofkCollectAuthorOfWork.objects.all()
        self.assertEqual(len(authors), 2)
        self.assertEqual(authors[1].iperson.primary_name, 'Someone')
