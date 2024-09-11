import functools
import logging

import numpy as np
from sklearn.cluster import KMeans

log = logging.getLogger(__name__)


def yield_all_cluster(X, X_ids, seed=42, target_group_size=800, min_k=4, max_k=100):
    cluster_fn = functools.partial(create_cluster, seed=seed, target_group_size=target_group_size, min_k=min_k,
                                   max_k=max_k)

    for lv1_indexes in cluster_fn(X):
        lv1_ids = X_ids[lv1_indexes]
        log.info(f'running lv2 clustering for {len(lv1_ids)}')
        for lv2_indexes in cluster_fn(X[lv1_indexes]):
            lv2_ids = lv1_ids[lv2_indexes]
            log.info(f'yielding {len(lv2_indexes)}')
            yield lv2_ids


def yield_all_cluster2(X, X_ids, seed=42, target_group_size=1000, max_k=100):
    cluster_fn = functools.partial(create_cluster, seed=seed, target_group_size=target_group_size,
                                   max_k=max_k)

    todo_list = [(X, X_ids)]
    while todo_list:
        cur_X, cur_X_ids = todo_list.pop()
        for indexes in cluster_fn(cur_X):
            ids = cur_X_ids[indexes]
            if len(ids) > target_group_size:
                todo_list.append((cur_X[indexes], ids))
            else:
                yield ids


def create_cluster(X, seed=42, target_group_size=800, max_k=100):
    """

    Parameters
    ----------
    X
    seed
    target_group_size
        outputs cluster could be larger than target_group_size
    max_k
        calculation time will be slow if max_k is too large

    Returns
    -------
    indexes:  bool array
        list of indexes for each cluster
    """
    k = X.shape[0] // target_group_size + 1
    if k < 2:
        log.info(f'Too few data, skip clustering k={k}  X.shape={X.shape}')
        yield np.ones(X.shape[0], dtype=bool)
        return
    k = min(k, max_k)

    log.info(f'k: {k}')
    log.info(f'X shape: {X.shape}')

    log.info('Clustering fitting')
    kmeans = KMeans(n_clusters=k, random_state=seed)
    kmeans.fit(X)

    log.info('Predict')
    labels = kmeans.predict(X)

    for label in range(k):
        yield labels == label
