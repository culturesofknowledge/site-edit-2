from django.db.models import OuterRef, Count
from django.db.models.functions import Coalesce

from location.models import CofkUnionLocation


def create_sql_count_work_by_location(rel_type_list):
    queryset = CofkUnionLocation.objects.filter(
        cofkworklocationmap__location_id=OuterRef('pk'),
        cofkworklocationmap__relationship_type__in=rel_type_list
    ).values('location_id').annotate(n_work=Count('location_id')).values_list('n_work')
    return Coalesce(queryset, 0)
