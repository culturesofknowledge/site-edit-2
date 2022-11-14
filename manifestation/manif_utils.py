from manifestation.models import CofkUnionManifestation


def get_recref_display_name(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id


def get_recref_target_id(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id
