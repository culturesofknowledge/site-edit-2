from core.helper import model_utils
from manifestation.models import CofkUnionManifestation


def get_recref_display_name(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id


def get_recref_target_id(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id


def create_manif_id(iwork_id) -> str:
    return f'W{iwork_id}-{model_utils.next_seq_safe("cofk_union_manif_manif_id_seq")}'
