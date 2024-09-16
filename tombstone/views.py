import dataclasses
import logging

from django.shortcuts import render
from django.urls import reverse

from location.models import CofkUnionLocation
from tombstone.features.dataset import work_features, location_features
from tombstone.services import tombstone
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


@dataclasses.dataclass
class WebCluster:
    records: list
    distance: float


@dataclasses.dataclass
class LocationWebCluster(WebCluster):
    @property
    def merge_ids(self):
        return [r.location_id for r in self.records]


def build_clusters(records, raw_df_maker, feature_maker,
                   cluster_factory=WebCluster,
                   n_top_clusters=100,
                   score_threshold=0.5):
    raw_df = raw_df_maker(records)
    feature_ids = raw_df.index.to_numpy()
    features = feature_maker(raw_df)
    clusters = tombstone.find_similar_clusters(features, feature_ids,
                                               score_threshold=score_threshold)[:n_top_clusters]
    id_works = {_id: work for _id, work in zip(feature_ids, records)}
    clusters = [
        cluster_factory(
            records=[id_works[_id] for _id in cluster.ids],
            distance=cluster.distance
        )
        for cluster in clusters
    ]
    return clusters


def home(request):
    return render(request, 'tombstone/tombstone_basic.html')


def similar_work(request):
    score_threshold = 0.1

    log.info('Preprocessing data')
    records = CofkUnionWork.objects.all()
    clusters = build_clusters(records,
                              work_features.prepare_raw_df,
                              work_features.create_features,
                              score_threshold=score_threshold)

    return render(request, 'tombstone/tombstone_work.html',
                  {'clusters': clusters})


def similar_location(request):
    score_threshold = 0.1

    log.info('Preprocessing data')
    records = CofkUnionLocation.objects.all()
    clusters = build_clusters(records,
                              location_features.prepare_raw_df,
                              location_features.create_features,
                              cluster_factory=LocationWebCluster,
                              score_threshold=score_threshold)

    return render(request, 'tombstone/tombstone_location.html',
                  {
                      'clusters': clusters,
                      'merge_page_url': reverse('location:merge'),
                  })
