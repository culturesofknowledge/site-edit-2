from core.models import CofkLookupCatalogue, CofkLookupDocumentType
from login.models import CofkUser


def create_username_map():
    user_map = {'Initial import': 'Initial import'}
    for val in ['cofksuper', 'postgres']:
        user_map[val] = 'SysAdmin'

    for user in CofkUser.objects.iterator():
        forename = user.forename or ''
        surname = user.surname or ''
        user_map[user.username] = (f'{forename.strip()} {surname.strip()}'
                                   if forename or surname else user.username)

    return user_map


def create_catalogue_status_map():
    return dict(CofkLookupCatalogue.objects.values_list('catalogue_code', 'publish_status').all())


def create_catalogue_name_map():
    return dict(CofkLookupCatalogue.objects.values_list('catalogue_code', 'catalogue_name').all())


def create_lookup_doc_desc_map():
    return dict(CofkLookupDocumentType.objects.values_list('document_type_code', 'document_type_desc').all())
