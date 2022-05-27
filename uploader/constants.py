

class DBMapping:
    """
    Helper class for mapping between Excel sheet, SQLAlchemy class name
    and Postgres table name.
    """
    def __init__(self, openoffice, postgres, sqlalchemy, _id=None):
        self.openoffice = openoffice
        self.sqlalchemy = sqlalchemy
        self.postgres = postgres
        self.id = _id


mapping = {'person': DBMapping('person', 'cofk_collect_person', 'CofkCollectPerson', 'iperson_id'),
           'location': DBMapping('location', 'cofk_collect_location', 'CofkCollectLocation', 'location_id'),
           'institution': DBMapping('institution', 'cofk_collect_institution', 'CofkCollectInstitution', 'institution_id'),
           'work': DBMapping('person', 'cofk_collect_work', 'CofkCollectWork', 'iwork_id'),
           'manifestation': DBMapping('person', 'cofk_collect_manifestation', 'CofkCollectManifestation', 'manifestation_id'),
           'addressee': DBMapping('addressee', 'cofk_collect_addressee_of_work', 'CofkCollectAddresseeOfWork'),
           'author': DBMapping('author', 'cofk_collect_author_of_work', 'CofkCollectAuthorOfWork'),
           'occupation_of_person': DBMapping('occupation_of_person', 'cofk_collect_occupation_of_person', 'CofkCollectOccupationOfPerson'),
           'person_mentioned': DBMapping('person', 'cofk_collect_person_mentioned_in_work', 'CofkCollectPersonMentionedInWork'),
           'place_mentioned': DBMapping('place_mentioned', 'cofk_collect_place_mentioned_in_work', 'CofkCollectPlaceMentionedInWork'),
           'language_of_work': DBMapping('language_of_work', 'cofk_collect_language_of_work', 'CofkCollectLanguageOfWork'),
           'subject_of_work': DBMapping('subject_of_work', 'cofk_collect_subject_of_work', 'CofkCollectSubjectOfWork'),
           'work_resource': DBMapping('work_resource', 'cofk_collect_work_resource', 'CofkCollectWorkResource'),
           'person_resource': DBMapping('person_resource', 'cofk_collect_person_resource', 'CofkCollectPersonResource'),
           'location_resource': DBMapping('location_resource', 'cofk_collect_location_resource', 'CofkCollectLocationResource'),
           'institution_resource': DBMapping('institution_resource', 'cofk_collect_institution_resource', 'CofkCollectInstitutionResource'),
           'image_of_manif': DBMapping('image_of_manif', 'cofk_collect_image_of_manif', 't_cofk_collect_image_of_manif'),
           }

# These are the sheets expected to be in every uploaded Excel file
mandatory_sheets = {'Work', 'Manifestation', 'People', 'Places', 'Repositories'}
