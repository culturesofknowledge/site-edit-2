ENTITIES = {
    'audit': 'audit',
    'institution': 'repository',
    'location': 'location',
    'manifestation': 'manifestation',
    'person': 'person',
    'publication': 'publication',
    'work': 'work',
}

SEARCH_LAYOUT_GRID = 'grid'
SEARCH_LAYOUT_TABLE = 'table'

REL_TYPE_COMMENT_REFERS_TO = 'refers_to'
REL_TYPE_COMMENT_AUTHOR = 'refers_to_author'
REL_TYPE_COMMENT_ADDRESSEE = 'refers_to_addressee'
REL_TYPE_COMMENT_DATE = 'refers_to_date'
REL_TYPE_COMMENT_ORIGIN = 'refers_to_origin'
REL_TYPE_COMMENT_DESTINATION = 'refers_to_destination'
REL_TYPE_COMMENT_ROUTE = 'route'
REL_TYPE_COMMENT_RECEIPT_DATE = 'refers_to_recept_date'
REL_TYPE_COMMENT_PERSON_MENTIONED = 'refers_to_people_mentioned_in_work'

REL_TYPE_MENTION_WORK = 'mentions_work'
REL_TYPE_MENTION_PLACE = 'mentions_place'
REL_TYPE_MENTION = 'mentions'  # for work -- person

REL_TYPE_WORK_IS_REPLY_TO = 'is_reply_to'
REL_TYPE_WORK_MATCHES = 'matches'

REL_TYPE_WAS_SENT_TO = 'was_sent_to'
REL_TYPE_WAS_SENT_FROM = 'was_sent_from'

REL_TYPE_FORMERLY_OWNED = 'formerly_owned'

REL_TYPE_ENCLOSED_IN = 'enclosed_in'

REL_TYPE_HANDWROTE = 'handwrote'

REL_TYPE_STORED_IN = 'stored_in'

REL_TYPE_IS_RELATED_TO = 'is_related_to'

REL_TYPE_DEALS_WITH = 'deals_with'

REL_TYPE_CREATED = 'created'
REL_TYPE_SENT = 'sent'
REL_TYPE_SIGNED = 'signed'

REL_TYPE_WAS_ADDRESSED_TO = 'was_addressed_to'
REL_TYPE_INTENDED_FOR = 'intended_for'

# rel_type person
REL_TYPE_MEMBER_OF = 'member_of'
REL_TYPE_PARENT_OF = 'parent_of'
REL_TYPE_EMPLOYED = 'employed'
REL_TYPE_TAUGHT = 'taught'
REL_TYPE_WAS_PATRON_OF = 'was_patron_of'

REL_TYPE_UNSPECIFIED_RELATIONSHIP_WITH = 'unspecified_relationship_with'
REL_TYPE_ACQUAINTANCE_OF = 'acquaintance_of'
REL_TYPE_WAS_BUSINESS_ASSOCIATE = 'was_a_business_associate_of'
REL_TYPE_COLLABORATED_WITH = 'collaborated_with'
REL_TYPE_COLLEAGUE_OF = 'colleague_of'
REL_TYPE_FRIEND_OF = 'friend_of'
REL_TYPE_RELATIVE_OF = 'relative_of'
REL_TYPE_SIBLING_OF = 'sibling_of'
REL_TYPE_SPOUSE_OF = 'spouse_of'

REL_TYPE_IMAGE_OF = 'image_of'

REL_TYPE_WAS_BORN_IN_LOCATION = 'was_born_in_location'
REL_TYPE_WAS_IN_LOCATION = 'was_in_location'
REL_TYPE_DIED_AT_LOCATION = 'died_at_location'

REL_TYPE_IS_MANIF_OF = 'is_manifestation_of'

DEFAULT_YEAR = 9999
DEFAULT_MONTH = 12
DEFAULT_DAY = 31
DEFAULT_EMPTY_DATE_STR = f'{DEFAULT_YEAR}-{DEFAULT_MONTH}-{DEFAULT_DAY}'
STD_DATE_FORMAT = '%Y-%m-%d'
SEARCH_DATE_FORMAT = '%d/%m/%Y'
SIMPLE_DATE_FORMAT = '%Y%m%d'
SEARCH_DATETIME_FORMAT = '%d/%m/%Y %H:%M'

DEFAULT_CHANGE_USER = '__unknown_user'

TRUE_CHAR = 'Y'

# permissions
PM_CHANGE_WORK = 'work.change_cofkunionwork'
PM_CHANGE_PERSON = 'person.change_cofkunionperson'
PM_CHANGE_PUBLICATION = 'publication.change_cofkunionpublication'
PM_CHANGE_LOCATION = 'location.change_cofkunionlocation'
PM_CHANGE_INST = 'institution.change_cofkunioninstitution'
PM_CHANGE_ROLECAT = 'core.change_cofkunionrolecategory'
PM_CHANGE_LOOKUPCAT = 'core.change_cofklookupcatalogue'
PM_CHANGE_SUBJECT = 'core.change_cofkunionsubject'
PM_CHANGE_ORGTYPE = 'core.change_cofkunionorgtype'
PM_CHANGE_COLLECTWORK = 'uploader.change_cofkcollectwork'

PM_CHANGE_USER = 'login.change_cofkuser'
PM_CHANGE_COMMENT = 'core.change_cofkunioncomment'

PM_VIEW_AUDIT = 'audit.view_cofkunionauditliteral'

PM_EXPORT_FILE_WORK = 'work.export_file'
PM_EXPORT_FILE_PERSON = 'person.export_file'
PM_EXPORT_FILE_LOCATION = 'location.export_file'
PM_EXPORT_FILE_INST = 'institution.export_file'
