"""
Main module for tombstone services.
Contain list of functions for tombstone services.
"""

import dataclasses
import logging

import numpy as np

from tombstone.services import linkage_cluster, tombstone_features, kmean_cluster
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


@dataclasses.dataclass
class WorkCluster:
    ids: np.ndarray
    distance: float


def example():
    score_threshold = 1.2
    n_inputs = 5000
    # n_inputs = None
    k = 100
    target_group_size = 1000

    works = CofkUnionWork.objects.all()
    if n_inputs:
        works = works[:n_inputs]
    clusters = find_similar_work_clusters(works, score_threshold, target_group_size)
    for cluster in clusters:
        print(f'{len(cluster.ids):>3} {cluster.distance:.3f} {cluster.ids[:5]}')


def find_similar_work_clusters(works, score_threshold=1.2, target_group_size=1000) -> list[WorkCluster]:
    work_raw_df = tombstone_features.prepare_work_raw_df(works)
    X_ids = work_raw_df.index.to_numpy()
    X = tombstone_features.create_features(work_raw_df)
    total_items = work_raw_df.shape[0]
    clusters = []
    group_ids_list = kmean_cluster.yield_all_cluster2(X, X_ids, target_group_size=target_group_size)
    group_ids_list = (ids for ids in group_ids_list if len(ids) > 1)
    for sub_group_ids in group_ids_list:
        log.debug(f'running linkage clustering for {len(sub_group_ids)}')
        sub_indexes = np.where(np.isin(X_ids, sub_group_ids))[0]
        sub_X = X[sub_indexes]
        sub_group_ids = X_ids[sub_indexes]
        nodes = list(linkage_cluster.cal_nodes(sub_X))
        for cluster in linkage_cluster.yield_cluster_indexes(nodes, score_threshold=score_threshold):
            cluster_group_ids = sub_group_ids[cluster.indexes]
            log.debug(f'cluster: {len(cluster.indexes):>5} {cluster.distance:.3f} {cluster_group_ids[:5]}...')
            clusters.append(WorkCluster(ids=cluster_group_ids, distance=cluster.distance))
    clusters = sorted(clusters, key=lambda c: c.distance)
    return clusters
