"""
Main module for clonefinder services.
Contain list of functions for clonefinder services.
"""

import dataclasses
import logging
import pickle

import numpy as np

from clonefinder.features.dataset import location_features
from clonefinder.models import ClonefinderRequest
from clonefinder.services import linkage_cluster, kmean_cluster, clonefinder_schedule
from location.models import CofkUnionLocation

log = logging.getLogger(__name__)


@dataclasses.dataclass
class IdsCluster:
    ids: np.ndarray
    distance: float


def example():
    score_threshold = 0.1
    n_inputs = 5000
    # n_inputs = None
    k = 100
    target_group_size = 1000

    locations = CofkUnionLocation.objects.all()
    location_raw_df = location_features.prepare_raw_df(locations)
    feature_ids = location_raw_df.index.to_numpy()
    features = location_features.create_features(location_raw_df)

    print(features.shape)
    print(type(features))
    return
    clusters = find_similar_clusters(features, feature_ids,
                                     score_threshold=score_threshold,
                                     target_group_size=target_group_size)
    for cluster in clusters:
        print(f'{len(cluster.ids):>3} {cluster.distance:.3f} {cluster.ids[:5]}')


def find_similar_clusters(features, feature_ids,
                          score_threshold=1.2, target_group_size=1000) -> list[IdsCluster]:
    assert features.shape[0] == feature_ids.shape[0]
    total_items = features.shape[0]
    clusters = []
    group_ids_list = kmean_cluster.yield_all_cluster(features, feature_ids, target_group_size=target_group_size)
    group_ids_list = (ids for ids in group_ids_list if len(ids) > 1)
    for sub_group_ids in group_ids_list:
        log.debug(f'running linkage clustering for {len(sub_group_ids)}')
        sub_indexes = np.where(np.isin(feature_ids, sub_group_ids))[0]
        sub_X = features[sub_indexes]
        sub_group_ids = feature_ids[sub_indexes]
        nodes = list(linkage_cluster.cal_nodes(sub_X))
        for cluster in linkage_cluster.yield_cluster_indexes(nodes, score_threshold=score_threshold):
            cluster_group_ids = sub_group_ids[cluster.indexes]
            log.debug(f'cluster: {len(cluster.indexes):>5} {cluster.distance:.3f} {cluster_group_ids[:5]}...')
            clusters.append(IdsCluster(ids=cluster_group_ids, distance=cluster.distance))
    clusters = sorted(clusters, key=lambda c: c.distance)
    return clusters


def create_clusters(raw_df, create_features, score_threshold=0.5, n_top_clusters=None) -> list[IdsCluster]:
    log.info(f'Preprocessing data {raw_df.shape}')
    feature_ids = raw_df.index.to_numpy()
    features = create_features(raw_df)

    log.info(f'Running clustering {features.shape}')
    clusters = find_similar_clusters(features, feature_ids, score_threshold=score_threshold)
    if n_top_clusters:
        clusters = clusters[:n_top_clusters]

    return clusters


def trigger_clustering(model_name, queryset, status_handler, username=None):
    """
    Create task for clonefinder background job to run clustering.
    """

    sql, sql_params = queryset.order_by().query.sql_with_params()

    task = ClonefinderRequest.objects.filter(model_name=model_name).first()
    if not task:
        task = ClonefinderRequest(model_name=model_name)
        if username:
            task.update_current_user_timestamp(username)
    task.sql = sql
    if sql_params:
        task.sql_params = pickle.dumps(sql_params)
    task.save()
    status_handler.mark_pending()
    if not clonefinder_schedule.status_handler.is_pending_or_running():
        clonefinder_schedule.status_handler.mark_pending()


def reset_all_status_handler():
    clonefinder_schedule.status_handler.reset()
    clonefinder_schedule.person_status_handler.reset()
    clonefinder_schedule.inst_status_handler.reset()
    clonefinder_schedule.location_status_handler.reset()
    clonefinder_schedule.work_status_handler.reset()
