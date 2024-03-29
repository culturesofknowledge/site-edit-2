'''
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
           'institution': DBMapping('institution', 'cofk_collect_institution', 'CofkCollectInstitution',
                                    'institution_id'),
           'work': DBMapping('person', 'cofk_collect_work', 'CofkCollectWork', 'iwork_id'),
           'manifestation': DBMapping('person', 'cofk_collect_manifestation', 'CofkCollectManifestation',
                                      'manifestation_id'),
           'addressee': DBMapping('addressee', 'cofk_collect_addressee_of_work', 'CofkCollectAddresseeOfWork'),
           'author': DBMapping('author', 'cofk_collect_author_of_work', 'CofkCollectAuthorOfWork'),
           'occupation_of_person': DBMapping('occupation_of_person', 'cofk_collect_occupation_of_person',
                                             'CofkCollectOccupationOfPerson'),
           'person_mentioned': DBMapping('person', 'cofk_collect_person_mentioned_in_work',
                                         'CofkCollectPersonMentionedInWork'),
           'place_mentioned': DBMapping('place_mentioned', 'cofk_collect_place_mentioned_in_work',
                                        'CofkCollectPlaceMentionedInWork'),
           'language_of_work': DBMapping('language_of_work', 'cofk_collect_language_of_work',
                                         'CofkCollectLanguageOfWork'),
           'subject_of_work': DBMapping('subject_of_work', 'cofk_collect_subject_of_work', 'CofkCollectSubjectOfWork'),
           'work_resource': DBMapping('work_resource', 'cofk_collect_work_resource', 'CofkCollectWorkResource'),
           'person_resource': DBMapping('person_resource', 'cofk_collect_person_resource', 'CofkCollectPersonResource'),
           'location_resource': DBMapping('location_resource', 'cofk_collect_location_resource',
                                          'CofkCollectLocationResource'),
           'institution_resource': DBMapping('institution_resource', 'cofk_collect_institution_resource',
                                             'CofkCollectInstitutionResource'),
           'image_of_manif': DBMapping('image_of_manif', 'cofk_collect_image_of_manif',
                                       't_cofk_collect_image_of_manif'),
           }
'''

SEPARATOR = ';'

# These are the sheets expected to be in every uploaded Excel file
# Sheet names are case-sensitive !!!!!!
# The first sheet must be Work
# combos must have the id column first!!!
MANDATORY_SHEETS = {
    'Work': {
        'columns': ['iwork_id', 'date_of_work_as_marked', 'original_calendar', 'date_of_work_std_year',
                    'date_of_work_std_month', 'date_of_work_std_day', 'date_of_work2_std_year',
                    'date_of_work2_std_month', 'date_of_work2_std_day', 'date_of_work_std_is_range',
                    'date_of_work_inferred', 'date_of_work_uncertain', 'date_of_work_approx', 'notes_on_date_of_work',
                    'author_names', 'author_ids', 'authors_as_marked', 'authors_inferred', 'authors_uncertain',
                    'notes_on_authors', 'addressee_names', 'addressee_ids', 'addressees_as_marked',
                    'addressees_inferred', 'addressees_uncertain', 'notes_on_addressees', 'origin_name', 'origin_id',
                    'origin_as_marked', 'origin_inferred', 'origin_uncertain', 'destination_name',
                    'destination_id', 'destination_as_marked', 'destination_inferred', 'destination_uncertain',
                    'abstract', 'keywords', 'language_id', 'language_of_work', 'hasgreek', 'hasarabic', 'hashebrew',
                    'haslatin', 'answererby', 'incipit', 'explicit', 'notes_on_letter', 'mention_id', 'emlo_mention_id',
                    'notes_on_people_mentioned', 'editors_notes', 'resource_name', 'resource_url', 'resource_details'],
        'ids': ['iwork_id', 'author_ids', 'addressee_ids', 'origin_id', 'emlo_mention_id'],
        'ints': ['iwork_id', 'date_of_work_std_year', 'date_of_work_std_month', 'date_of_work_std_day',
                 'date_of_work2_std_year', 'date_of_work2_std_month', 'date_of_work2_std_day', 'origin_id',
                 'destination_id'],
        'bools': ['date_of_work_std_is_range', 'date_of_work_inferred', 'date_of_work_uncertain', 'date_of_work_approx',
                  'authors_inferred', 'authors_uncertain', 'addressees_inferred', 'addressees_uncertain',
                  'origin_inferred', 'origin_uncertain', 'destination_inferred', 'destination_uncertain',
                  'hasgreek', 'hasarabic', 'hashebrew', 'haslatin'],
        'strings': [('date_of_work_as_marked', 250), ('original_calendar', 2), 'notes_on_letter',
                    'notes_on_people_mentioned', 'author_names', 'notes_on_authors', 'mention_id', 'origin_name',
                    'destination_name'],
        'required': ['iwork_id'],
        'combos': [('author_ids', 'author_names'), ('addressee_ids', 'addressee_names'),
                   ('emlo_mention_id', 'mention_id')],
        'years': ['date_of_work_std_year', 'date_of_work2_std_year'],
        'months': ['date_of_work_std_month', 'date_of_work2_std_month'],
        'dates': ['date_of_work_std_day', 'date_of_work2_std_day'],
        'ranges': [{'date_of_work_std_is_range': [('date_of_work_std_year', 'date_of_work2_std_year')]}]
    },
    'Manifestation': {
        'columns': ['manifestation_id', 'iwork_id', 'manifestation_type', 'repository_id', 'repository_name',
                    'id_number_or_shelfmark', 'manifestation_notes', 'manifestation_type_p', 'printed_edition_details',
                    'printed_edition_notes', 'ms_translation', 'printed_translation'],
        'ids': ['manifestation_id', 'repository_id'],
        'ints': ['manifestation_id', 'repository_id'],
        'strings': [('manifestation_type', 3), ('id_number_or_shelfmark', 500), 'manifestation_notes'],
        'required': ['iwork_id']
    },
    'People': {
        'columns': ['primary_name', 'iperson_id', 'editors_notes'],
        'ids': ['iperson_id'],
        'combos': [('iperson_id', 'primary_name')],
        'required': ['primary_name'],
        'strings': [('primary_name', 200)]
    },
    'Places': {
        'columns': ['location_name', 'location_id'],
        'required': ['location_name'],
        'ids': ['location_id'],
        'combos': [('location_id', 'location_name')],
        'strings': [('location_name', 500)]
    },
    'Repositories': {
        'columns': ['institution_name', 'institution_id', 'institution_city', 'institution_country'],
        'ids': ['institution_id'],
        'required': ['institution_name'],
        'strings': ['institution_name', 'institution_city', 'institution_country']
    }
}

MAX_YEAR = 1900
MIN_YEAR = 1400
