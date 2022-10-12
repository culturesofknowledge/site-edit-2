from person.models import CofkUnionPerson


def get_recref_display_name(person: CofkUnionPerson):
    return person and person.foaf_name


def get_recref_target_id(person: CofkUnionPerson):
    return person and person.person_id
