import warnings

from core.models import CofkLookupCatalogue
from work import work_utils
from work.models import CofkUnionQueryableWork, CofkUnionWork

work_dict_a = dict(
    work_id='fixture_work_id_a',
    description='description value',
    origin_as_marked='origin_as_marked value',
    abstract='abstract value',
    keywords='keywords value',
    editors_notes='work_dict_a.editors_notes',
    date_of_work_std_year=1122,
    date_of_work_std_month=11,
    date_of_work_std_day=22,
    date_of_work_as_marked='work_dict_a.date_of_work_as_marked',
)

work_dict_b = dict(
    work_id='fixture_work_id_b',
    description='description value',
    origin_as_marked='origin_as_marked value',
    abstract='abstract value',
    keywords='keywords value',
)


def fixture_queryable_work() -> CofkUnionQueryableWork:
    warnings.warn('queryable_work is deprecated', DeprecationWarning)
    work = CofkUnionWork(description='test')
    work.save()

    q_work = work_utils.clone_queryable_work(work, _return=True)
    return q_work


def fixture_work_by_dict(work_dict: dict) -> CofkUnionWork:
    work = CofkUnionWork(**work_dict)
    work.save()

    q_work = work_utils.clone_queryable_work(work, _return=True)
    return work
