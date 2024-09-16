"""
Main module for tombstone services.
Contain list of functions for tombstone services.
"""

import dataclasses
import logging

import numpy as np

from location.models import CofkUnionLocation
from tombstone.features.dataset import location_features
from tombstone.services import linkage_cluster, kmean_cluster

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
    group_ids_list = kmean_cluster.yield_all_cluster2(features, feature_ids, target_group_size=target_group_size)
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
