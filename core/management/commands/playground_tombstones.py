import logging

import numpy as np
from django.core.management import BaseCommand
from scipy.cluster.hierarchy import linkage, dendrogram

from tombstone.services import tombstone
from tombstone.services.kmean_cluster import yield_all_cluster
from tombstone.services.linkage_cluster import yield_cluster_indexes, ClusterTreeMaker
from tombstone.services.tombstone_features import prepare_work_raw_df, create_features

# from core.management.commands.exporter import InstFrontendCsv

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for n in ['matplotlib', 'PIL']:
            logging.getLogger(n).setLevel(logging.WARNING)

        # main41()
        # main39__main_kmean()
        # main38__try_linkage()
        tombstone.example()
        # main40()


def main41():
    labels = np.array([1, 1, 2, 2, 3, 3, 3])
    data = np.array([10, 20, 30, 40, 50, 60, 70])

    print(data[labels == 2])


def main40():
    data = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    y = [30, 80, 90]
    indexes = np.searchsorted(data, y)
    print(indexes)
    print(data[indexes])
    # indexes2 = np.where(data, y)
    # print(indexes2)


def main43():
    # n_inputs = 10000
    n_inputs = None
    k = 100

    work_raw_df = prepare_work_raw_df(n=n_inputs)
    X_ids = work_raw_df.index
    X = create_features(work_raw_df)
    total_items = 0
    for group_ids in yield_all_cluster(X, X_ids):
        n_items = group_ids.shape[0]
        print(f'{n_items} {group_ids[:5]}')
        total_items += n_items
    assert total_items == X.shape[0], f'{total_items} != {X.shape[0]}'


def main39__main_kmean():
    # n_inputs = 10000
    n_inputs = None
    k = 100

    work_raw_df = prepare_work_raw_df(n=n_inputs)
    X_ids = work_raw_df.index
    X = create_features(work_raw_df)
    total_items = 0
    for group_ids in yield_all_cluster(X, X_ids):
        n_items = group_ids.shape[0]
        print(f'{n_items} {group_ids[:5]}')
        total_items += n_items
    assert total_items == X.shape[0], f'{total_items} != {X.shape[0]}'


def plot_dendrogram(Z, labels):
    # Plot the dendrogram
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 7))
    plt.title('Hierarchical Clustering Dendrogram for Mixed Features')
    dendrogram(Z,
               leaf_rotation=90.,
               leaf_font_size=12.,
               labels=labels,
               )
    plt.xlabel('Sample index')
    plt.ylabel('Distance')
    plt.show()


def main38__try_linkage():
    n_inputs = 5000
    score_threshold = 1.1

    work_raw_df = prepare_work_raw_df(n=n_inputs)
    X_ids = work_raw_df.index.to_numpy()
    X = create_features(work_raw_df)

    log.info('Clustering')
    Z = linkage(X.toarray(), 'ward')

    # nodes = {}
    # _id = X.shape[0] - 1
    # for z in Z:
    #     _id += 1
    #     left_id, right_id, distance, count = z
    #     left_id = int(left_id)
    #     right_id = int(right_id)
    #     nodes[_id] = ClusterNode(
    #         left=nodes.get(left_id, left_id),
    #         right=nodes.get(right_id, right_id),
    #         distance=distance,
    #         id=_id,
    #         count=count,
    #     )
    #
    #     print(z)

    id_map = list(range(n_inputs))

    def _id_convertor(i):
        return id_map[i]

    nodes = ClusterTreeMaker().make_tree(Z, n_inputs).values()
    # # yield_cluster_indexes(nodes, score_threshold=score_threshold, ids=X_ids)
    # if ids is None:
    #     leafs_ids = leafs_indexes
    # else:
    #     leafs_ids = ids[leafs_indexes]

    for cluster in yield_cluster_indexes(nodes, score_threshold=score_threshold):
        print(f'-----------------------------')
        leafs_ids = X_ids[cluster.indexes]
        print(leafs_ids)
        print(f'count: {leafs_ids.shape[0]:.0f}, distance: {cluster.distance:.4f}')
        # print(leafs_indexes)
        # print(f'count: {leafs_indexes.shape[0]:.0f}, distance: {node.distance:.4f}')

    # nodes = list(nodes)
    # while nodes:
    #     node = nodes.pop()
    #     print(f'-----------------------------')
    #     node.print_all_leafs(_id_convertor)
    #
    #     for sub_node in [node.left, node.right]:
    #         if isinstance(sub_node, ClusterNode):
    #             nodes.append(sub_node)

    # log.info('Plotting dendrogram')
    # plot_dendrogram(Z, labels=[f'{i}' for i in range(n_inputs)])
    # print(CofkUnionWork.objects.count())
