import json
import logging
import pickle

from cllib import inspect_utils
from clonefinder.features.dataset import inst_features, person_features, location_features, work_features
from clonefinder.models import ClonefinderRequest
from clonefinder.services import clonefinder
from core.helper import task_serv
from core.helper.model_serv import default_current_timestamp
from core.helper.task_serv import FileBaseTaskStatusHandler
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from person.models import CofkUnionPerson
from work.models import CofkUnionWork

log = logging.getLogger(__name__)

status_handler = FileBaseTaskStatusHandler(name='clonefinder_clustering_flag')

work_status_handler = FileBaseTaskStatusHandler(name='clonefinder_work_flag')
location_status_handler = FileBaseTaskStatusHandler(name='clonefinder_location_flag')
person_status_handler = FileBaseTaskStatusHandler(name='clonefinder_person_flag')
inst_status_handler = FileBaseTaskStatusHandler(name='clonefinder_inst_flag')


def run_clustering(model_class, fields, prepare_raw_df, create_features, score_threshold=0.5,
                   n_top_clusters=100):
    tasks = ClonefinderRequest.objects.filter(model_name=model_class.__name__).all()
    for task in tasks:
        params = None
        if task.sql_params:
            params = pickle.loads(task.sql_params)
        records = model_class.objects.raw(task.sql, params)
        records = [{k: getattr(r, k, None) for k in fields}
                   for r in records]
        raw_df = prepare_raw_df(records)

        clusters = clonefinder.create_clusters(raw_df, create_features, score_threshold=score_threshold,
                                             n_top_clusters=n_top_clusters)
        json_strs = [cluster_result_to_json_str(c) for c in clusters]
        result_jsonl = '\n'.join(json_strs)

        task.status = 1
        task.result_jsonl = result_jsonl
        task.change_timestamp = default_current_timestamp()
        task.save()


def run_inst_clustering():
    run_clustering(CofkUnionInstitution,
                   inst_features.REQUIRED_FIELDS,
                   inst_features.prepare_raw_df,
                   inst_features.create_features,
                   )


def run_person_clustering():
    run_clustering(CofkUnionPerson,
                   person_features.REQUIRED_FIELDS,
                   person_features.prepare_raw_df,
                   person_features.create_features,
                   score_threshold=0.002,
                   n_top_clusters=200)


def run_location_clustering():
    run_clustering(CofkUnionLocation,
                   location_features.REQUIRED_FIELDS,
                   location_features.prepare_raw_df,
                   location_features.create_features)


def run_work_clustering():
    run_clustering(CofkUnionWork,
                   work_features.REQUIRED_FIELDS,
                   work_features.prepare_raw_df,
                   work_features.create_features,
                   score_threshold=0.1,
                   n_top_clusters=200)


def cluster_result_to_json_str(cluster):
    obj = {'ids': [int(i) for i in cluster.ids], 'distance': float(cluster.distance)}
    json_str = json.dumps(obj)
    return json_str


def run_all_clustering():
    def run_task_fn():
        task_serv.run_task(run_work_clustering, work_status_handler)
        task_serv.run_task(run_person_clustering, person_status_handler)
        task_serv.run_task(run_location_clustering, location_status_handler)
        task_serv.run_task(run_inst_clustering, inst_status_handler)

    log.debug('Checking for clustering tasks')
    task_serv.run_task(run_task_fn, status_handler)


RUN_CLONEFINDER_CLUSTERING_FN = inspect_utils.get_fn_path(run_all_clustering)
