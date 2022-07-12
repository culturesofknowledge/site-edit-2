from location.models import CofkUnionLocation

location_dict_a = dict(
    location_name='location_name value',
    element_1_eg_room='element_1_eg_room value',
    element_2_eg_building='element_2_eg_building value',
    element_3_eg_parish='element_3_eg_parish value',
    element_4_eg_city='element_4_eg_city value',
    element_5_eg_county='element_5_eg_county value',
    element_6_eg_country='element_6_eg_country value',
    element_7_eg_empire='element_7_eg_empire value',
    editors_notes='editors_notes value',
    location_synonyms='location_synonyms value',
    latitude='latitude value',
    longitude='longitude value',
)

loc_res_dict_a = {
    'resource_name': 'resource_name a',
    'resource_url': 'resource_url a',
    'resource_details': 'resource_details a',
}


def create_location_a():
    return CofkUnionLocation(**location_dict_a)
