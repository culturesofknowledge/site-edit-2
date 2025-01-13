import uuid

from person.models import CofkUnionPerson

person_min_dict_a = dict(
    foaf_name='person aaaa',
)

person_dict_a = dict(
    person_id='person_aaaa',
    foaf_name='person aaaa',
    gender='M',
    skos_altlabel='skos_altlabel aaa',
    person_aliases='person_aliases aaa',
    further_reading='further_reading aaa',
    editors_notes='editors_notes aaa',
    date_of_birth_year=1921,
    iperson_id=90000001,
)

person_dict_b = dict(
    person_id='person_bbbb',
    foaf_name='person bbbb',
    gender='F',
    skos_altlabel='skos_altlabel bbb',
    person_aliases='person_aliases bbb',
    further_reading='further_reading bbb',
    editors_notes='editors_notes bbb',
    date_of_death_year=1922,
    iperson_id=90000002,
)


def create_person_obj():
    return create_person_obj_by_dict(person_min_dict_a)


def create_person_obj_by_dict(person_dict: dict):
    obj = CofkUnionPerson(**person_dict, init_seq_id=True)
    obj.pk = uuid.uuid4()
    return obj
