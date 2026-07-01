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
        'ids': ['iwork_id', 'author_ids', 'addressee_ids', 'origin_id', 'destination_id', 'emlo_mention_id'],
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
        'ranges': [{'date_of_work_std_is_range': [('date_of_work_std_year', 'date_of_work2_std_year')]}],
        'notes': ['notes_on_date_of_work'],
        'keywords': ['keywords'],
    },
    'Manifestation': {
        'columns': ['manifestation_id', 'iwork_id', 'manifestation_type', 'repository_id', 'repository_name',
                    'id_number_or_shelfmark', 'manifestation_notes', 'manifestation_type_p', 'printed_edition_details',
                    'printed_edition_notes', 'ms_translation', 'printed_translation'],
        'ids': ['manifestation_id', 'repository_id'],
        'ints': ['manifestation_id', 'repository_id'],
        'strings': [('manifestation_type', 3), ('id_number_or_shelfmark', 500), 'manifestation_notes'],
        'required': ['iwork_id'],
        'shelfmarks': ['id_number_or_shelfmark'],
        'bibliographies': ['printed_edition_details'],
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

# Column definitions for bulk work corrections upload.
# Sheet name is lowercase 'work' (distinguishes from the standard 'Work' new-works upload).
# Keys are the exact spreadsheet column header strings; values are CofkUnionWork field names.
# 'Original Catalogue name' is a special FK field requiring a CofkLookupCatalogue lookup.
# Columns not present in this dict (e.g. Author, Recipient full names, Languages) are ignored.
CORRECTION_WORK_SHEET = {
    'identifier': 'EMLO Letter ID Number',
    'command_col': 'Command',
    'columns': {
        'Year date': 'date_of_work_std_year',
        'Month date': 'date_of_work_std_month',
        'Day date': 'date_of_work_std_day',
        'Date is range (0=No; 1=Yes)': 'date_of_work_std_is_range',
        'Year 2nd date (range)': 'date_of_work2_std_year',
        'Month 2nd date (range)': 'date_of_work2_std_month',
        'Day 2nd date (range)': 'date_of_work2_std_day',
        'Calendar of date provided to EMLO': 'original_calendar',
        'Date as marked on letter': 'date_of_work_as_marked',
        'Date uncertain (0=No; 1=Yes)': 'date_of_work_uncertain',
        'Date approximate (0=No; 1=Yes)': 'date_of_work_approx',
        'Date inferred (0=No; 1=Yes)': 'date_of_work_inferred',
        'Notes on date': 'notes_on_date_of_work',
        'Author as marked in body/text of letter': 'authors_as_marked',
        'Author inferred (0=No; 1=Yes)': 'authors_inferred',
        'Author uncertain (0=No; 1=Yes)': 'authors_uncertain',
        'Recipient as marked in body/text of letter': 'addressees_as_marked',
        'Recipient inferred (0=No; 1=Yes)': 'addressees_inferred',
        'Recipient uncertain (0=No; 1=Yes)': 'addressees_uncertain',
        'Origin as marked in body/text of letter': 'origin_as_marked',
        'Origin inferred (0=No; 1=Yes)': 'origin_inferred',
        'Origin uncertain (0=No; 1=Yes)': 'origin_uncertain',
        'Destination as marked in body/text of letter': 'destination_as_marked',
        'Destination inferred (0=No; 1=Yes)': 'destination_inferred',
        'Destination uncertain (0=No; 1=Yes)': 'destination_uncertain',
        'Abstract': 'abstract',
        'Keywords': 'keywords',
        'Incipit': 'incipit',
        'Explicit': 'explicit',
        'Original Catalogue name': 'original_catalogue',  # FK — resolved via CofkLookupCatalogue
        'Source': 'accession_code',
        #'General notes for public display': 'notes_on_letter',
        "Editors' working notes": 'editors_notes',
    },
    'ints': [
        'date_of_work_std_year', 'date_of_work_std_month', 'date_of_work_std_day',
        'date_of_work2_std_year', 'date_of_work2_std_month', 'date_of_work2_std_day',
    ],
    'bools': [
        'date_of_work_std_is_range', 'date_of_work_uncertain', 'date_of_work_approx',
        'date_of_work_inferred', 'authors_inferred', 'authors_uncertain',
        'addressees_inferred', 'addressees_uncertain',
        'origin_inferred', 'origin_uncertain', 'destination_inferred', 'destination_uncertain',
    ],
    'years': ['date_of_work_std_year', 'date_of_work2_std_year'],
    'months': ['date_of_work_std_month', 'date_of_work2_std_month'],
    'dates': ['date_of_work_std_day', 'date_of_work2_std_day'],
    'fk_fields': ['original_catalogue'],
}

# Column definitions for bulk People upload (BULKnewPEOPLErecordsTEMPLATE format).
# Columns are mapped by position (index) rather than by matching header text, because the
# template uses verbose human-readable column headers.
BULK_PEOPLE_SHEET = {
    'columns': [
        'primary_name',
        'alternative_names',
        'roles_or_titles',
        'gender',
        'is_organisation',
        'date_of_birth_year',
        'date_of_birth_month',
        'date_of_birth_day',
        'date_of_birth_is_range',
        'date_of_birth2_year',
        'date_of_birth2_month',
        'date_of_birth2_day',
        'date_of_birth_inferred',
        'date_of_birth_uncertain',
        'date_of_birth_approx',
        'date_of_death_year',
        'date_of_death_month',
        'date_of_death_day',
        'date_of_death_is_range',
        'date_of_death2_year',
        'date_of_death2_month',
        'date_of_death2_day',
        'date_of_death_inferred',
        'date_of_death_uncertain',
        'date_of_death_approx',
        'flourished_year',
        'flourished_month',
        'flourished_day',
        'flourished_is_range',
        'flourished2_year',
        'flourished2_month',
        'flourished2_day',
        'notes_on_person',
        'editors_notes',
    ],
    'required': ['primary_name'],
    'strings': [('primary_name', 200), ('gender', 1), ('is_organisation', 1),
                'alternative_names', 'roles_or_titles', 'notes_on_person',
                'editors_notes'],
    'ints': ['date_of_birth_year', 'date_of_birth_month', 'date_of_birth_day',
             'date_of_birth2_year', 'date_of_birth2_month', 'date_of_birth2_day',
             'date_of_death_year', 'date_of_death_month', 'date_of_death_day',
             'date_of_death2_year', 'date_of_death2_month', 'date_of_death2_day',
             'flourished_year', 'flourished_month', 'flourished_day',
             'flourished2_year', 'flourished2_month', 'flourished2_day'],
    'bools': ['date_of_birth_is_range', 'date_of_birth_inferred', 'date_of_birth_uncertain', 'date_of_birth_approx',
              'date_of_death_is_range', 'date_of_death_inferred', 'date_of_death_uncertain', 'date_of_death_approx',
              'flourished_is_range'],
    'years': ['date_of_birth_year', 'date_of_birth2_year', 'date_of_death_year', 'date_of_death2_year',
              'flourished_year', 'flourished2_year'],
    'months': ['date_of_birth_month', 'date_of_birth2_month', 'date_of_death_month', 'date_of_death2_month',
               'flourished_month', 'flourished2_month'],
    'dates': ['date_of_birth_day', 'date_of_birth2_day', 'date_of_death_day', 'date_of_death2_day',
              'flourished_day', 'flourished2_day'],
}

def normalize_header(text) -> str:
    """Normalize a spreadsheet header for lookup: take the first line and strip whitespace."""
    if not text:
        return ''
    return str(text).split('\n')[0].strip()


# Maps verbose header text from BULKnewPEOPLErecordsTEMPLATE to CofkCollectPerson field names.
# Keys are the normalized first line of each column header (see normalize_header()).
# Columns with no corresponding model field are omitted (flourished inferred/uncertain/approx,
# resource_name/url, further reading).
BULK_PEOPLE_HEADER_MAP = {
    'Primary name': 'primary_name',
    'Synonyms (separated by semi-colon)': 'alternative_names',
    'Occupations, role, titles (separated by semi-colon)': 'roles_or_titles',
    'GENDER': 'gender',
    'IS ORGANIZATION': 'is_organisation',
    'BIRTH YEAR / FOUNDATION YEAR IF ORG': 'date_of_birth_year',
    'BIRTH/FOUNDATION YEAR INFERRED': 'date_of_birth_inferred',
    'BIRTH/FOUNDATION YEAR UNCERTAIN': 'date_of_birth_uncertain',
    'BIRTH/FOUNDATION YEAR APPROX': 'date_of_birth_approx',
    'DEATH YEAR / DISBAND YEAR IF ORG': 'date_of_death_year',
    'DEATH/DISBAND YEAR INFERRED': 'date_of_death_inferred',
    'DEATH/DISBAND YEAR UNCERTAIN': 'date_of_death_uncertain',
    'DEATH/DISBAND YEAR APPROX.': 'date_of_death_approx',
    'FLOURISHED EARLIEST YEAR 1': 'flourished_year',
    'FLOURISHED LATEST YEAR 2': 'flourished2_year',
    'FLOURISHED IS RANGE': 'flourished_is_range',
    "GENERAL NOTES ON PERSON (Researcher's note: for public display; full grammatical sentences, please)": 'notes_on_person',
    "EDITORS' NOTES AND QUERIES (not to be published in public interface; these are working notes)": 'editors_notes',
}

# Maps verbose header text from BULKnewLOCATIONrecordsTEMPLATE to CofkCollectLocation field names.
BULK_LOCATIONS_HEADER_MAP = {
    'Name of City/town/village [human settlement]': 'element_4_eg_city',
    'Name of County': 'element_5_eg_county',
    'Name of Country': 'element_6_eg_country',
    'Name of District of city (if required)': 'element_3_eg_parish',
    'Name of Building (if required)': 'element_2_eg_building',
    'Name of Room (if required)': 'element_1_eg_room',
    'Name of Empire (if required)': 'element_7_eg_empire',
    'Synonyms/Alternative names for location (separated by semi-colon)': 'location_synonyms',
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude',
    'GENERAL NOTES ON PLACE (for public display; full grammatical sentences, please)': 'notes_on_place',
    "EDITORS' NOTES AND QUERIES (not to be published in public interface; these are working notes)": 'editors_notes',
}

# Column definitions for bulk Locations upload (BULKnewLOCATIONrecordsTEMPLATE format).
BULK_LOCATIONS_SHEET = {
    'columns': [
        'element_4_eg_city',
        'element_5_eg_county',
        'element_6_eg_country',
        'element_3_eg_parish',
        'element_2_eg_building',
        'element_1_eg_room',
        'element_7_eg_empire',
        'location_synonyms',
        'latitude',
        'longitude',
        'notes_on_place',
        'editors_notes',
    ],
    'required': [],
    'strings': [('element_4_eg_city', 100), ('element_5_eg_county', 100), ('element_6_eg_country', 100),
                ('element_3_eg_parish', 100), ('element_2_eg_building', 100), ('element_1_eg_room', 100),
                ('element_7_eg_empire', 100), 'location_synonyms', 'notes_on_place',
                'editors_notes'],
}
