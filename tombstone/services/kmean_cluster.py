import functools
import logging

import numpy as np
from sklearn.cluster import KMeans

log = logging.getLogger(__name__)


def yield_all_cluster(X, X_ids, seed=42, target_group_size=1000, max_k=100, max_depth=5):
    cluster_fn = functools.partial(create_cluster, seed=seed, target_group_size=target_group_size,
                                   max_k=max_k)

    todo_list = [(X, X_ids, 0)]
    while todo_list:
        cur_X, cur_X_ids, depth = todo_list.pop()
        if depth >= max_depth:
            yield cur_X_ids
            continue

        for indexes in cluster_fn(cur_X):
            ids = cur_X_ids[indexes]
            if len(ids) > target_group_size:
                todo_list.append((cur_X[indexes], ids, depth + 1))
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
    labels = kmeans.labels_
    for label in range(k):
        label_matched = labels == label
        log.info(f'cluster {label} size: {label_matched.sum()}')
        yield label_matched
