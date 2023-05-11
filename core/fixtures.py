from core.models import CofkLookupCatalogue

res_dict_a = {
    'resource_name': 'resource_name a',
    'resource_url': 'resource_url a',
    'resource_details': 'resource_details a',
}

res_dict_b = {
    'resource_name': 'resource_name b',
    'resource_url': 'resource_url b',
    'resource_details': 'resource_details b',
}

comment_dict_a = {
    'comment': 'yooooooooooooooooooo',
}

lang_dict_eng = {
    'code_639_3': 'eng',
    'code_639_1': 'en',
    'language_name': 'English',
}

lang_dict_ara = {
    'code_639_3': 'ara',
    'code_639_1': 'ar',
    'language_name': 'Arabic',
}


def fixture_default_lookup_catalogue():
    c = CofkLookupCatalogue()
    c.catalogue_name = 'test'
    c.catalogue_code = ''
    c.is_in_union = 1
    c.publish_status = 1
    c.save()
    return c
