from typing import Union

from django.urls import reverse

from core.helper import model_serv, query_cache_serv, data_serv
from manifestation.models import CofkUnionManifestation
from work.forms import manif_type_choices


def get_form_url(manif: CofkUnionManifestation):
    try:
        return reverse('work:manif_update', kwargs={
            'iwork_id': manif.work.iwork_id,
            'manif_id': manif.manifestation_id,
        })
    except:
        return ''


def get_recref_display_name(manif: CofkUnionManifestation):
    return manif and (manif.id_number_or_shelfmark or manif.manifestation_id)


def get_rich_display_name(manif: CofkUnionManifestation):
    """Return a rich display name for a manifestation including its type, shelfmark, and associated work details."""
    if not manif:
        return ''
    from work import work_serv
    type_display = dict(manif_type_choices).get(manif.manifestation_type, '')
    shelfmark = manif.id_number_or_shelfmark or ''
    parts = []
    if type_display:
        parts.append(type_display)
    if shelfmark:
        parts.append(shelfmark)
    label = ': '.join(parts) if parts else manif.manifestation_id
    if manif.work:
        work = manif.work
        work_display = work_serv.get_recref_display_name(work)
        label += f' -- Work ID {work.iwork_id}, {work_display}'
    return label


def get_recref_target_id(manif: CofkUnionManifestation):
    return manif and manif.manifestation_id


def create_manif_id(iwork_id) -> str:
    return f'W{iwork_id}-{model_serv.next_seq_safe("cofk_union_manif_manif_id_seq")}'


def get_doctype_desc(manif: Union['CofkUnionManifestation', 'CofkCollectManifestation']) -> str:
    return query_cache_serv.create_lookup_doc_desc_map().get(manif.manifestation_type, manif.manifestation_type)


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
        shelfmark = enclosed_in.id_number_or_shelfmark or enclosed_in.manifestation_id
        url = get_form_url(enclosed_in)
        link = data_serv.endcode_url_content(url, shelfmark) if url else shelfmark
        manifestation_summary.append(f' ~ Was enclosed in: {link}')

    for encloses in manif.find_encloses():
        shelfmark = encloses.id_number_or_shelfmark or encloses.manifestation_id
        url = get_form_url(encloses)
        link = data_serv.endcode_url_content(url, shelfmark) if url else shelfmark
        manifestation_summary.append(f' ~ Had enclosure: {link}')

    return manifestation_summary
