from django.contrib.auth.models import Group

from cllib_django.query_utils import load_cache  # noqa
from core.models import CofkLookupCatalogue, CofkLookupDocumentType
from login.models import CofkUser

ck_all_union_relationship_types = 'all_union_relationship_types'


def create_username_map():
    def _fn():
        user_map = {'Initial import': 'Initial import'}
        for val in ['cofksuper', 'postgres']:
            user_map[val] = 'SysAdmin'

        for user in CofkUser.objects.iterator():
            forename = user.forename or ''
            surname = user.surname or ''
            user_map[user.username] = (f'{forename.strip()} {surname.strip()}'
                                       if forename or surname else user.username)

        return user_map

    return load_cache('username_map', _fn)


def create_catalogue_status_map():
    return load_cache(
        'catalogue_status_map',
        lambda: dict(CofkLookupCatalogue.objects.values_list('catalogue_code', 'publish_status').all())
    )


def create_catalogue_name_map():
    return load_cache(
        'catalogue_name_map',
        lambda: dict(CofkLookupCatalogue.objects.values_list('catalogue_code', 'catalogue_name').all())
    )


def create_lookup_doc_desc_map():
    return load_cache(
        'lookup_doc_desc_map',
        lambda: dict(CofkLookupDocumentType.objects.values_list('document_type_code', 'document_type_desc').all())
    )


def create_group_name_id_map() -> dict[dict, int]:
    return load_cache(
        'group_name_id_map',
        lambda: dict(Group.objects.values_list('name', 'id').all())
    )
