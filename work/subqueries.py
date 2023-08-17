from django.db.models import OuterRef, Case, When, Value

from core.models import CofkLookupDocumentType
from sharedlib.djangolib import query_utils
from work.models import CofkUnionWork


def create_joined_person_ann_field(relationship_types):
    """
    make person searchable by StringAgg and concat target fields
    one work can have multiple person, that is reason why we need to use StringAgg

    list of target fields should be same as output in frontend
    which should be able to find in CofkUnionPerson.to_string
    """
    subquery = CofkUnionWork.objects.filter(
        cofkworkpersonmap__work_id=OuterRef('pk'),
        cofkworkpersonmap__relationship_type__in=relationship_types,
    ).annotate(**{
        '_death_range': Case(When(cofkworkpersonmap__person__date_of_death_is_range=1, then=Value(' or after')),
                             default=Value('')),
        '_birth_range': Case(When(cofkworkpersonmap__person__date_of_birth_is_range=1, then=Value(' or before')),
                             default=Value('')),
        'person_detail': query_utils.join_values_for_search([
            'cofkworkpersonmap__person__foaf_name',
            'cofkworkpersonmap__person__date_of_birth_year',
            '_birth_range',
            'cofkworkpersonmap__person__date_of_death_year',
            '_death_range',
            'cofkworkpersonmap__person__skos_altlabel',
            'cofkworkpersonmap__person__person_aliases',
        ]),
    }).values_list('person_detail', flat=True)
    return subquery


def create_joined_location_ann_field(relationship_types, target_fields: list[str]):
    subquery = CofkUnionWork.objects.filter(
        cofkworklocationmap__work_id=OuterRef('pk'),
        cofkworklocationmap__relationship_type__in=relationship_types,
    ).annotate(**{
        'location_detail': query_utils.join_values_for_search([
            'cofkworklocationmap__location__location_name',
            'origin_as_marked',
            'destination_as_marked',
        ])
    }).values_list('location_detail', flat=True)
    return subquery


def create_joined_manif_ann_field():
    subquery = CofkUnionWork.objects.filter(
        manif_set__work_id=OuterRef('pk'),
    ).annotate(
        _doctype_desc=(CofkLookupDocumentType.objects
                       .filter(document_type_code=OuterRef('manif_set__manifestation_type'))
                       .values_list('document_type_desc', flat=True)),
        manif_detail=query_utils.join_values_for_search([
            '_doctype_desc',
            'manif_set__postage_marks',
            'manif_set__cofkmanifinstmap_set__inst__institution_name',
            'manif_set__id_number_or_shelfmark',
            'manif_set__printed_edition_details',
            'manif_set__manifestation_incipit',
            'manif_set__manifestation_excipit',
            'manif_set__manif_from_set__manif_to__id_number_or_shelfmark',
            'manif_set__manif_to_set__manif_from__id_number_or_shelfmark',
        ])
    ).values_list('manif_detail', flat=True)
    return subquery


