from core.models import CofkLookupCatalogue
from work import work_utils
from work.models import CofkUnionQueryableWork, CofkUnionWork

work_dict_a = dict(
    work_id='work_id value',
    description='description value',
    origin_as_marked='origin_as_marked value',
    abstract='abstract value',
    keywords='keywords value',
)


def fixture_queryable_work() -> CofkUnionQueryableWork:
    work = CofkUnionWork(description='test')
    work.save()

    q_work = work_utils.clone_queryable_work(work, _return=True)
    return q_work


