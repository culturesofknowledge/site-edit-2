from django.urls import path, reverse
from django.utils.http import urlencode

VNAME_INIT_FORM = 'init_form'
VNAME_FULL_FORM = 'full_form'
VNAME_DELETE = 'delete'

VNAME_SEARCH = 'search'
VNAME_HOME = 'home'

VNAME_MERGE_CHOICE = 'merge'
VNAME_MERGE_ACTION = 'merge_action'
VNAME_MERGE_CONFIRM = 'merge_confirm'

VNAME_QUICK_INIT = 'quick_init'
VNAME_RETURN_QUICK_INIT = 'return_quick_init'


def create_common_urls_for_section(
        init_view=None,
        edit_view=None,
        delete_view=None,
        search_view=None,
        merge_view=None,
        merge_action_view=None,
        merge_confirm_view=None,
        edit_id_name='pk',
) -> list:
    if edit_view is None:
        edit_view = init_view

    paths = []
    if init_view is not None:
        paths.append(path('form', init_view, name=VNAME_INIT_FORM))
    if edit_view is not None:
        paths.append(path(f'form/<int:{edit_id_name}>', edit_view, name=VNAME_FULL_FORM))
    if delete_view is not None:
        paths.append(path('delete/<int:obj_id>', delete_view, name=VNAME_DELETE))
    if search_view is not None:
        paths.append(path('search', search_view, name=VNAME_SEARCH))
        paths.append(path('', search_view, name=VNAME_HOME))
    if merge_view is not None:
        paths.append(path('merge', merge_view, name=VNAME_MERGE_CHOICE))
    if merge_action_view is not None:
        paths.append(path('merge/action', merge_action_view, name=VNAME_MERGE_ACTION))
    if merge_confirm_view is not None:
        paths.append(path('merge/confirm', merge_confirm_view, name=VNAME_MERGE_CONFIRM))
    return paths


def create_urls_for_quick_init(quick_init_view, return_quick_init_view):
    return [
        path('quick_init', quick_init_view, name=VNAME_QUICK_INIT),
        path('return_quick_init/<pk>', return_quick_init_view, name=VNAME_RETURN_QUICK_INIT),
    ]


def build_url_query(url, query):
    return f'{url}?' + urlencode(query)


def reverse_url_by_request(vname, request):
    return reverse(f'{request.resolver_match.namespace}:{vname}')
