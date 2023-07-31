from typing import Union

from core.helper import model_serv
from core.models import CofkLookupDocumentType
from manifestation.models import CofkUnionManifestation


def get_recref_display_name(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id


def get_recref_target_id(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id


def create_manif_id(iwork_id) -> str:
    return f'W{iwork_id}-{model_serv.next_seq_safe("cofk_union_manif_manif_id_seq")}'


def get_doctype_desc(manif: Union['CofkUnionManifestation', 'CofkCollectManifestation']) -> str:
    if doctype := CofkLookupDocumentType.objects.filter(document_type_code=manif.manifestation_type).first():
        return doctype.document_type_desc
    else:
        return manif.manifestation_type


def get_manif_details(manif: CofkUnionManifestation) -> list[str]:
    first_line = get_doctype_desc(manif) + '. '
    if manif.postage_marks:
        first_line += f'Postmark: {manif.postage_marks}. '

    if manif_inst := manif.find_selected_inst():
        first_line += manif_inst.inst.institution_name

    if manif_inst and manif.id_number_or_shelfmark:
        first_line += ': '

    if manif.id_number_or_shelfmark:
        first_line += manif.id_number_or_shelfmark

    if manif.printed_edition_details:
        first_line += f' {manif.printed_edition_details}'

    manifestation_summary = [first_line]
    if manif.manifestation_incipit:
        manifestation_summary.append(f' ~ Incipit: {manif.manifestation_incipit}.')

    if manif.manifestation_excipit:
        manifestation_summary.append(f' ~ Excipit: {manif.manifestation_excipit}.')

    for enclosed_in in manif.find_enclosed_in():
        manifestation_summary.append(f' ~ {enclosed_in.id_number_or_shelfmark}')

    for encloses in manif.find_encloses():
        manifestation_summary.append(f' ~ {encloses.id_number_or_shelfmark}')

    return manifestation_summary
