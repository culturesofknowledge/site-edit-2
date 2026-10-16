from django.contrib.auth.models import Group

from cllib_django.query_utils import load_cache  # noqa
from core.models import CofkLookupCatalogue, CofkLookupDocumentType
from core import constant
from login.models import CofkUser

ck_all_union_relationship_types = 'all_union_relationship_types'


def user_display_name(user: CofkUser) -> str:
    """Resolve the name to display for a user.

    1. forename and surname -> both, combined
    2. only one of them -> whichever is available
    3. neither -> the local part of the email
    4. nothing usable -> the username
    """
    names = [(user.forename or '').strip(), (user.surname or '').strip()]
    name = ' '.join(n for n in names if n)
    if name:
        return name

    email = (user.email or '').strip()
    if email:
        local_part = email.split('@')[0].strip()
        if local_part:
            return local_part

    return user.username


def create_username_map():
    def _fn():
        user_map = {'Initial import': 'Initial import'}
        for val in ['cofksuper', 'postgres']:
            user_map[val] = 'SysAdmin'

        for user in CofkUser.objects.iterator():
            user_map[user.username] = user_display_name(user)

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
        constant.CACHE_GROUP_MAP_ID,
        lambda: dict(Group.objects.values_list('name', 'id').all())
    )
