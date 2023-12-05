from typing import Type, Iterable

from django.db import models
from django.db.models import Count, Q
from django.db.models.expressions import OuterRef
from django.db.models.functions import Coalesce

from cllib_django import query_utils
from core.constant import REL_TYPE_MENTION
from core.helper import query_serv
from person.models import CofkUnionPerson
from work import work_serv
from work.forms import AuthorRelationChoices, AddresseeRelationChoices


def create_sql_count_work_by_person(rel_type_list):
    queryset = CofkUnionPerson.objects.filter(
        work_serv.q_visible_works('cofkworkpersonmap__work'),
        cofkworkpersonmap__person_id=OuterRef('pk'),
        cofkworkpersonmap__relationship_type__in=rel_type_list
    ).values('pk').annotate(n_work=Count('pk')).values_list('n_work')
    return Coalesce(queryset, 0)


def create_queryset_by_queries(model_class: Type[models.Model], queries: Iterable[Q] = None, sort_by=None):
    queryset = model_class.objects
    annotate = {
        'sent': create_sql_count_work_by_person(AuthorRelationChoices.values),
        'recd': create_sql_count_work_by_person(AddresseeRelationChoices.values),
        'all_works': create_sql_count_work_by_person(
            AuthorRelationChoices.values + AddresseeRelationChoices.values),
        'mentioned': create_sql_count_work_by_person([REL_TYPE_MENTION]),

        'rolenames': CofkUnionPerson.objects.filter(
            cofkpersonrolemap__person_id=OuterRef('pk'),
        )
        .annotate(_rolenames=query_utils.join_values_for_search('cofkpersonrolemap__role__role_category_desc'))
        .values_list('_rolenames', flat=True),
        'names_and_titles': query_utils.concat_safe(
            [
                'foaf_name',
                'skos_altlabel',
                'person_aliases',
                'rolenames',
            ]
        )

    }

    queryset = query_serv.update_queryset(queryset, model_class, queries=queries,
                                          annotate=annotate, sort_by=sort_by)
    queryset = queryset.prefetch_related(
        'cofkpersonlocationmap_set__location',
        'cofkpersoncommentmap_set__comment',
        'roles',
        'resources',
        'images',
        'comments',
        'active_relationships__related',
        'passive_relationships__person',
    )

    return queryset
