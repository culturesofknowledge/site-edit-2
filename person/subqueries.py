from django.db.models import Count, Q
from django.db.models.expressions import OuterRef
from django.db.models.functions import Coalesce

from person.models import CofkUnionPerson
from work.models import CofkUnionWork


def create_sql_count_work_by_person(rel_type_list, work_q: Q = None):
    """
    work_q
        if given, only count works matching this filter (relative to CofkUnionWork)
    """
    filters = {}
    if work_q is not None:
        filters['cofkworkpersonmap__work__in'] = CofkUnionWork.objects.filter(work_q).values('pk')
    queryset = CofkUnionPerson.objects.filter(
        cofkworkpersonmap__person_id=OuterRef('pk'),
        cofkworkpersonmap__relationship_type__in=rel_type_list,
        **filters,
    ).values('pk').annotate(n_work=Count('pk')).values_list('n_work')
    return Coalesce(queryset, 0)


