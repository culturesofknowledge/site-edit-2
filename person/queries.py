from django.db.models import Count
from django.db.models.expressions import OuterRef
from django.db.models.functions import Coalesce

from person.models import CofkUnionPerson
from work import work_utils


def create_sql_count_work_by_person(rel_type_list):
    queryset = CofkUnionPerson.objects.filter(
        work_utils.q_visible_works('cofkworkpersonmap__work'),
        cofkworkpersonmap__person_id=OuterRef('pk'),
        cofkworkpersonmap__relationship_type__in=rel_type_list
    ).values('pk').annotate(n_work=Count('pk')).values_list('n_work')
    return Coalesce(queryset, 0)
