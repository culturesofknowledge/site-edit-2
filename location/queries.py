from django.db.models import OuterRef, Count
from django.db.models.functions import Coalesce

from location.models import CofkUnionLocation
from work import work_serv


def create_sql_count_work_by_location(rel_type_list):
    queryset = CofkUnionLocation.objects.filter(
        work_serv.q_visible_works('cofkworklocationmap__work'),
        cofkworklocationmap__location_id=OuterRef('pk'),
        cofkworklocationmap__relationship_type__in=rel_type_list
    ).values('location_id').annotate(n_work=Count('location_id')).values_list('n_work')
    return Coalesce(queryset, 0)
