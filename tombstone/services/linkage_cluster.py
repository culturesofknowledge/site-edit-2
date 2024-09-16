import dataclasses
import logging
from typing import Iterable

import numpy as np
from scipy.cluster.hierarchy import linkage

log = logging.getLogger(__name__)


@dataclasses.dataclass
class LinkageClusterResult:
    indexes: np.ndarray
    distance: float


def yield_cluster_indexes(nodes, score_threshold=1) -> Iterable[LinkageClusterResult]:
    nodes = list(nodes)
    while nodes:
        node = nodes.pop()
        if node.distance < score_threshold or node.count <= 2:
            leafs_indexes = node.find_all_leafs_indexes()
            yield LinkageClusterResult(indexes=leafs_indexes, distance=node.distance)
            continue

        for sub_node in [node.left, node.right]:
            if isinstance(sub_node, ClusterNode):
                nodes.append(sub_node)


class ClusterNode:
    def __init__(self, left, right, distance, id, count):
        self.left: ClusterNode | int = left
        self.right: ClusterNode | int = right
        self.distance = distance
        self.id = id
        self.count = count

    def __str__(self):
        return f'left: {self.left}, right: {self.right}, distance: {self.distance}, id: {self.id}, count: {self.count}'

    def find_all_leafs_indexes(self):
        leafs = []
        for node in [self.left, self.right]:
            if isinstance(node, int):
                leafs.append(node)
            else:
                leafs.extend(node.find_all_leafs_indexes())

        assert len(leafs) == self.count
        return np.array(leafs)

    # def print_all_leafs(self, id_convertor=None):
    #     leafs = self.find_all_leafs()
    #     if id_convertor:
    #         leafs = [id_convertor(i) for i in leafs]
    #     print(leafs)
    #     print(f'count: {self.count:.0f}, distance: {self.distance:.4f}')


class ClusterTreeMaker:

    def __init__(self):
        self._nodes = {}

    @property
    def nodes(self):
        """
        Output of maker, contains list of trees
        """
        return self._nodes

    def _pop_node(self, node_id):
        if node_id in self.nodes:
            return self.nodes.pop(node_id)
        else:
            return node_id

    def make_tree(self, Z, n_leafs):
        log.info('Building cluster nodes')
        self._nodes = {}
        _id = n_leafs - 1
        for z in Z:
            _id += 1
            left_id, right_id, distance, count = z
            left_id = int(left_id)
            right_id = int(right_id)

            self.nodes[_id] = ClusterNode(
                left=self._pop_node(left_id),
                right=self._pop_node(right_id),
                distance=distance,
                id=_id,
                count=count,
            )

        return self.nodes


def cal_nodes(X: np.ndarray, method='single'):
    log.info('Clustering')
    Z = linkage(X, method=method)
    nodes = ClusterTreeMaker().make_tree(Z, X.shape[0]).values()
    return nodes
