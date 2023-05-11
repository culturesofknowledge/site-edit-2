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
location_dict_b = dict(
    location_name='location_name value 2',
    element_1_eg_room='element_1_eg_room value 2',
    element_2_eg_building='element_2_eg_building value 2',
    element_3_eg_parish='element_3_eg_parish value 2',
    element_4_eg_city='element_4_eg_city value 2',
    element_5_eg_county='element_5_eg_county value 2',
    element_6_eg_country='element_6_eg_country value 2',
    element_7_eg_empire='element_7_eg_empire value 2',
    editors_notes='editors_notes value 2',
    location_synonyms='location_synonyms value 2',
    latitude='latitude value 2',
    longitude='longitude value 2',
)


def create_location_a() -> CofkUnionLocation:
    return create_location_obj_by_dict(location_dict_a)


def create_location_obj_by_dict(location_dict: dict) -> CofkUnionLocation:
    return CofkUnionLocation(**location_dict)
