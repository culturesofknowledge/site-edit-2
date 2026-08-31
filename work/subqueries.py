from django.contrib.postgres.aggregates import StringAgg
from django.db.models import OuterRef, Case, When, Value, BooleanField, Exists, TextField, Q, F
from django.db.models.functions import Cast, Concat, Coalesce

from core.constant import REL_TYPE_ENCLOSED_IN
from core.models import CofkLookupDocumentType
from work.models import CofkUnionWork


def _concat_safe(items, delimiter: str = None):
    if delimiter:
        new_items = []
        for i, item in enumerate(items):
            new_items.append(item)
            if i < len(items) - 1:
                new_items.append(Value(delimiter))
        items = new_items

    return Concat(
        *[Cast(f, TextField()) for f in items]
    )


def _join_values_for_search(fields, delimiter: str = None, agg_delimiter: str = ''):
    if isinstance(fields, list):
        fields = _concat_safe(fields, delimiter=delimiter)

    return StringAgg(fields, agg_delimiter, default=Value(''), output_field=TextField())


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
        '_birth_year': Cast('cofkworkpersonmap__person__date_of_birth_year', TextField()),
        '_death_year': Cast('cofkworkpersonmap__person__date_of_death_year', TextField()),
        '_birth_str': Concat(F('_birth_year'), F('_birth_range'), output_field=TextField()),
        '_death_str': Concat(F('_death_year'), F('_death_range'), output_field=TextField()),
        '_year_detail': Case(
            When(Q(cofkworkpersonmap__person__date_of_birth_year__isnull=False) &
                 Q(cofkworkpersonmap__person__date_of_death_year__isnull=False),
                 then=Concat(F('_birth_str'), Value('-'), F('_death_str'), output_field=TextField())),
            When(cofkworkpersonmap__person__date_of_birth_year__isnull=False,
                 then=Concat(Value('b. '), F('_birth_str'), output_field=TextField())),
            When(cofkworkpersonmap__person__date_of_death_year__isnull=False,
                 then=Concat(Value('d. '), F('_death_str'), output_field=TextField())),
            default=Value(''),
            output_field=TextField(),
        ),
        'person_detail': _join_values_for_search([
            'cofkworkpersonmap__person__foaf_name',
            '_year_detail',
            'cofkworkpersonmap__person__skos_altlabel',
            'cofkworkpersonmap__person__person_aliases',
        ], delimiter=', ', agg_delimiter=' '),
    }).values_list('person_detail', flat=True)
    return subquery


def create_joined_location_ann_field(relationship_types, target_fields: list[str]):
    """
    Build a subquery that aggregates related locations' searchable text for a work.

    The list of target_fields is concatenated (preserving order) to form the
    searchable value. Callers must pass fully-qualified field paths they want
    included, e.g. 'cofkworklocationmap__location__location_name',
    'cofkworklocationmap__location__location_synonyms', 'origin_as_marked', etc.
    """
    subquery = CofkUnionWork.objects.filter(
        cofkworklocationmap__work_id=OuterRef('pk'),
        cofkworklocationmap__relationship_type__in=relationship_types,
    ).annotate(**{
        'location_detail': _join_values_for_search(target_fields, delimiter=' ', agg_delimiter=' '),
    }).values_list('location_detail', flat=True)
    return subquery


def _prefixed_enclosure_field(fk_path, shelfmark_field, label):
    """Return a Case expression that prepends `label` when an enclosure relationship exists."""
    return Case(
        When(
            **{f'{fk_path}__relationship_type': REL_TYPE_ENCLOSED_IN},
            then=Concat(Value(label), Cast(shelfmark_field, TextField()), output_field=TextField()),
        ),
        default=Value(''),
        output_field=TextField(),
    )


def create_joined_manif_ann_field():
    subquery = CofkUnionWork.objects.filter(
        manif_set__work_id=OuterRef('pk'),
    ).annotate(
        _doctype_desc=(CofkLookupDocumentType.objects
                       .filter(document_type_code=OuterRef('manif_set__manifestation_type'))
                       .values_list('document_type_desc', flat=True)),
        _had_enclosure=_prefixed_enclosure_field(
           'manif_set__manif_to_set',
            'manif_set__manif_to_set__manif_from__id_number_or_shelfmark',
            'Had enclosure: ',
        ),
        _was_enclosed_in=_prefixed_enclosure_field(
            'manif_set__manif_from_set',
            'manif_set__manif_from_set__manif_to__id_number_or_shelfmark',
            'Was enclosed in: ',
        ),
        manif_detail=_join_values_for_search([
            '_doctype_desc',
            'manif_set__postage_marks',
            'manif_set__cofkmanifinstmap_set__inst__institution_name',
            'manif_set__id_number_or_shelfmark',
            'manif_set__printed_edition_details',
            'manif_set__manifestation_incipit',
            'manif_set__manifestation_excipit',
            '_had_enclosure',
            '_was_enclosed_in',
        ], delimiter=' ', agg_delimiter=' ')
    ).values_list('manif_detail', flat=True)
    return subquery

def is_owner_of_catalogue(user):
    return Case(
        When(original_catalogue__owner=user, then=Value(True)),
        default=Value(False),
        output_field=BooleanField(),
    )


