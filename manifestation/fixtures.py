from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation

manif_dict_a = dict(
    manifestation_id='manif_id_a',
    manifestation_type='ABC',
    id_number_or_shelfmark='id_number_or_shelfmark a',
    manifestation_creation_date_is_range=0,
    postage_marks='postage_marks a',
    printed_edition_details='printed_edition_details a',
)


def create_manif_obj_by_dict(manif_dict: dict) -> CofkUnionManifestation:
    return CofkUnionManifestation(**manif_dict)
