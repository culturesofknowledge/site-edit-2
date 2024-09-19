import dataclasses
import itertools
import json
import logging
import typing

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.helper.model_serv import ModelLike
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from person.models import CofkUnionPerson
from tombstone.features.dataset import work_features, location_features, person_features
from tombstone.models import TombstoneRequest
from tombstone.services import tombstone, tombstone_schedule
from tombstone.services.tombstone import IdsCluster
from tombstone.services.tombstone_schedule import inst_status_handler
from work.models import CofkUnionWork

log = logging.getLogger(__name__)

N_TOP_CLUSTERS = 100


@dataclasses.dataclass
class WebCluster:
    records: list[ModelLike]
    distance: float


@dataclasses.dataclass
class LocationWebCluster(WebCluster):
    @property
    def merge_ids(self):
        return [r.location_id for r in self.records]


@dataclasses.dataclass
class PersonWebCluster(WebCluster):
    @property
    def merge_ids(self):
        return [r.iperson_id for r in self.records]


@dataclasses.dataclass
class InstWebCluster(WebCluster):
    @property
    def merge_ids(self):
        return [r.institution_id for r in self.records]


WebClusterLike = typing.TypeVar('WebClusterLike', bound=WebCluster)


def find_clusters(raw_df, feature_maker,
                  n_top_clusters=N_TOP_CLUSTERS,
                  score_threshold=0.5):
    feature_ids = raw_df.index.to_numpy()
    features = feature_maker(raw_df)
    clusters = tombstone.find_similar_clusters(features, feature_ids,
                                               score_threshold=score_threshold)[:n_top_clusters]
    return clusters


def build_display_clusters(clusters: list[IdsCluster], cluster_factory, create_id_records_dict):
    clusters = list(clusters)
    id_record_dict = create_id_records_dict(itertools.chain.from_iterable(cluster.ids for cluster in clusters))
    clusters = [
        cluster_factory(
            records=[id_record_dict[_id] for _id in cluster.ids],
            distance=cluster.distance
        )
        for cluster in clusters
    ]
    return clusters


def home(request):
    return render(request, 'tombstone/tombstone_basic.html')


def render_tombstone_cluster(request, raw_df, create_features, create_id_records_dict, template_name,
                             score_threshold=0.1, cluster_factory=WebCluster, merge_page_url=None):
    log.info('Preprocessing data')
    clusters = find_clusters(raw_df,
                             create_features,
                             score_threshold=score_threshold)
    clusters = build_display_clusters(clusters, cluster_factory, create_id_records_dict)
    return render_cluster_results(request, template_name, clusters, merge_page_url)


def render_cluster_results(request, template_name, clusters: list[WebClusterLike], merge_page_url=None,
                           is_running=False, last_update_at=None):
    return render(request, template_name,
                  {
                      'clusters': clusters,
                      'merge_page_url': merge_page_url,
                      'is_running': is_running,
                      'last_update_at': last_update_at,
                  })


def similar_work(request):
    def _create_id_records_dict(ids):
        return {r.iwork_id: r for r in CofkUnionWork.objects.filter(iwork_id__in=ids)}

    records = CofkUnionWork.objects.all().values(*(list(work_features.FIELD_EXTRACTORS.keys()) + ['iwork_id']))
    raw_df = work_features.prepare_raw_df(records)
    return render_tombstone_cluster(request, raw_df, work_features.create_features, _create_id_records_dict,
                                    'tombstone/tombstone_work.html')


def similar_location(request):
    def _create_id_records_dict(ids):
        return {r.location_id: r for r in CofkUnionLocation.objects.filter(location_id__in=ids)}

    records = CofkUnionLocation.objects.all().values(
        *(list(location_features.FIELD_EXTRACTORS.keys()) + ['location_id']))
    raw_df = location_features.prepare_raw_df(records)
    return render_tombstone_cluster(request, raw_df, location_features.create_features, _create_id_records_dict,
                                    'tombstone/tombstone_location.html',
                                    merge_page_url=reverse('location:merge'),
                                    cluster_factory=LocationWebCluster)


def similar_person(request):
    def _create_id_records_dict(ids):
        return {r.iperson_id: r for r in CofkUnionPerson.objects.filter(iperson_id__in=ids)}

    score_threshold = 0.002
    records = CofkUnionPerson.objects.all().values(
        *('iperson_id', 'date_of_birth', 'date_of_death', 'foaf_name', 'skos_altlabel',
          'skos_hiddenlabel', 'person_aliases',))
    raw_df = person_features.prepare_raw_df(records)
    return render_tombstone_cluster(request, raw_df, person_features.create_features, _create_id_records_dict,
                                    'tombstone/tombstone_person.html', merge_page_url=reverse('person:merge'),
                                    score_threshold=score_threshold,
                                    cluster_factory=PersonWebCluster)


def similar_inst(request):
    def _create_id_records_dict(ids):
        return {r.institution_id: r for r in CofkUnionInstitution.objects.filter(institution_id__in=ids)}

    record = TombstoneRequest.objects.filter(model_name=CofkUnionInstitution.__name__).first()
    clusters = []
    last_update_at = None
    if record and record.result_jsonl:
        clusters = record.result_jsonl.split('\n')
        clusters = (json.loads(cluster) for cluster in clusters)
        clusters = (IdsCluster(ids=cluster['ids'], distance=cluster['distance']) for cluster in clusters)
        clusters = build_display_clusters(clusters, InstWebCluster, _create_id_records_dict)
        last_update_at = record.change_timestamp

    return render_cluster_results(request, 'tombstone/tombstone_inst.html',
                                  clusters,
                                  merge_page_url=reverse('institution:merge'),
                                  is_running=inst_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


@require_POST
def trigger_inst_clustering(request):
    task = TombstoneRequest.objects.filter(model_name=CofkUnionInstitution.__name__).first()
    if not task:
        task = TombstoneRequest(model_name=CofkUnionInstitution.__name__)
        task.update_current_user_timestamp(request.user.username)
    task.sql = str(CofkUnionInstitution.objects.filter().query)
    task.save()
    inst_status_handler.mark_pending()
    if not tombstone_schedule.status_handler.is_pending_or_running():
        tombstone_schedule.status_handler.mark_pending()

    return redirect('tombstone:inst')
