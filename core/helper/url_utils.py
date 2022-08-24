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
    if merge_view is not None:
        paths.append(path('merge', merge_view, name='merge'))
    return paths
