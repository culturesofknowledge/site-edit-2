import json
import logging

from cllib import inspect_utils
from core.helper import task_serv
from core.helper.model_serv import default_current_timestamp
from core.helper.task_serv import FileBaseTaskStatusHandler
from institution.models import CofkUnionInstitution
from tombstone.features.dataset import inst_features
from tombstone.models import TombstoneRequest

log = logging.getLogger(__name__)

status_handler = FileBaseTaskStatusHandler(name='tombstone_clustering_flag')

work_status_handler = FileBaseTaskStatusHandler(name='tombstone_work_flag')
location_status_handler = FileBaseTaskStatusHandler(name='tombstone_location_flag')
person_status_handler = FileBaseTaskStatusHandler(name='tombstone_person_flag')
inst_status_handler = FileBaseTaskStatusHandler(name='tombstone_inst_flag')


def create_clusters(raw_df, create_features, score_threshold=0.5):
    from tombstone.views import find_clusters  # KTODO to be migrated to tombstone.services.tombstone
    log.info('Preprocessing data')
    clusters = find_clusters(raw_df,
                             create_features,
                             score_threshold=score_threshold)
    return clusters


def run_inst_clustering():

    tasks = TombstoneRequest.objects.filter(model_name=CofkUnionInstitution.__name__).all()
    for task in tasks:
        keys = (
            'institution_id',
            'institution_name',
            'institution_synonyms',
            'institution_city',
            'institution_country',
        )
        records = [{k: getattr(r, k, None) for k in keys}
                   for r in CofkUnionInstitution.objects.raw(task.sql)]
        raw_df = inst_features.prepare_raw_df(records)

        clusters = create_clusters(raw_df, inst_features.create_features)

        json_strs = [cluster_result_to_json_str(c) for c in clusters]
        result_jsonl = '\n'.join(json_strs)

        task.status = 1
        task.result_jsonl = result_jsonl
        task.change_timestamp = default_current_timestamp()
        task.save()


def cluster_result_to_json_str(cluster):
    obj = {'ids': [int(i) for i in cluster.ids], 'distance': float(cluster.distance)}
    json_str = json.dumps(obj)
    return json_str


def run_tombstone_clustering():
    log.info('Tombstone clustering triggered')
    print(RUN_TOMBSTONE_CLUSTERING_FN)

    def run_task_fn():
        task_serv.run_task(run_inst_clustering, inst_status_handler)

    task_serv.run_task(run_task_fn, status_handler)


RUN_TOMBSTONE_CLUSTERING_FN = inspect_utils.get_fn_path(run_tombstone_clustering)
