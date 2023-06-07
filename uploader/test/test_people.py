import logging
from django.utils import timezone

from core.models import Iso639LanguageCode
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from person.models import  CofkUnionPerson
from uploader.models import CofkCollectUpload, CofkCollectStatus, CofkCollectAuthorOfWork
from uploader.spreadsheet import CofkUploadExcelFile
from uploader.test.test_utils import UploaderTestCase

log = logging.getLogger(__name__)

class TestPeople(UploaderTestCase):

    def setUp(self) -> None:
        super().setUp()
        CofkCollectStatus.objects.create(status_id=1,
                                         status_desc='Awaiting review')

        CofkUnionLocation(pk=782).save()

        for lang in ['eng', 'fra']:
            Iso639LanguageCode(code_639_3=lang).save()

        CofkUnionInstitution(institution_id=1,
                             institution_name='Bodleian',
                             institution_city='Oxford').save()

        for person in [{'person_id': 'a', 'iperson_id': 15257, 'foaf_name': 'Newton'},
                       {'person_id': 'b', 'iperson_id': 885, 'foaf_name': 'Baskerville'},
                       {'person_id': 'c', 'iperson_id': 22859, 'foaf_name': 'Wren'}]:
            CofkUnionPerson(**person).save()

        CofkUnionLocation(location_id=400285).save()

        self.new_upload = CofkCollectUpload()
        self.new_upload.upload_status_id = 1
        self.new_upload.uploader_email = 'test@user.com'
        self.new_upload.upload_timestamp = timezone.now()
        self.new_upload.save()

    def test_extra_person_no_union(self):
        """
        This test provides two a person, Baskerville with an id that does not exist in the union
        database.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton", "15257", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "test", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
             85, "test", "test", "EMLO", "http://emlo.bodleian.ox.ac.uk/", "Early Modern Letters Online test"]],
            'People': [["Baskerville", 85],
                       ["newton", 15257],
                       ["Wren", 22859] ,],
            'Places': [['Burford', 400285],
                       ['Carisbrooke', 782]],
            'Manifestation': [[1, 1, "ALS", 1, "Bodleian", "test", "test", '', '', '', '', ''],
                              [2, 1, '', '', '', '', '', "P", "test", "test", '', '']],
            'Repositories': [['Bodleian', 1]]}
        filename = self.create_excel_file(data)

        cuef = CofkUploadExcelFile(self.new_upload, filename)

        self.assertIn('There is no person with the id 85 in the Union catalogue.',
                      cuef.errors['work']['errors'][0]['errors'])


    def test_extra_person_omit_author_id_semicolon(self):
        """
        This test provides two author names listed, newton;Someone but only one id, 15257, and no
        semi-colon for the id. This should raise an error.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton;Someone", "15257", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "test", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
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
             "test", 1, 1, "test", "test", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
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

        self.assertIn('Column author_ids in Work sheet contains a non-valid value.',
                      cuef.errors['work']['errors'][0]['errors'])

    def test_extra_person(self):
        """
        This test provides two author names listed, newton;Someone and one id, 15257 but containing a semi-colon for
        the ids to indicate a new person should be created.
        This should not raise an error.
        """
        data = {'Work': [
            [1, "test", "J", 1660, 1, 1, 1660, 1, 2, 1, 1, 1, 1, "test", "newton;Someone", "15257;", "test", 1, 1,
             "test", "Wren", 22859, "test", 1, 1, "test", "Burford", 400285, "test", 1, 1, "Carisbrooke", 782,
             "test", 1, 1, "test", "test", "fra;eng", '', '', '', '', '', '', "test", "test", "test", "Baskerville",
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