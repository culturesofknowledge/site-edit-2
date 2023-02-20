institution_dict_a = dict(
    institution_name='aaaa'
)


def create_person_obj():
    from .models import CofkUnionInstitution
    return CofkUnionInstitution(**institution_dict_a)
