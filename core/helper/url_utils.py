from django.urls import path


def create_common_urls_for_section(
        init_view=None,
        edit_view=None,
        search_view=None,
        merge_view=None,
        edit_id_name='pk',
) -> list:
    if edit_view is None:
        edit_view = init_view

    paths = []
    if init_view is not None:
        paths.append(path('form', init_view, name='init_form'))
    if edit_view is not None:
        paths.append(path(f'form/<int:{edit_id_name}>', edit_view, name='full_form'))
    if search_view is not None:
        paths.append(path('search', search_view, name='search'))
        paths.append(path('', search_view, name='home'))
    if merge_view is not None:
        paths.append(path('merge', merge_view, name='merge'))
    return paths


def create_urls_for_quick_init(quick_init_view, return_quick_init_view):
    return [
        path('quick_init', quick_init_view, name='quick_init'),
        path('return_quick_init/<pk>', return_quick_init_view, name='return_quick_init'),
    ]
