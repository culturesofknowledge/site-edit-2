from institution.models import CofkUnionInstitution


def get_recref_display_name(inst: CofkUnionInstitution):
    return inst and inst.institution_name


def get_recref_target_id(inst: CofkUnionInstitution):
    return inst and inst.institution_id
