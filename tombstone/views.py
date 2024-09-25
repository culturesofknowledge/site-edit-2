import dataclasses
import itertools
import json
import logging
import typing

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from core import constant
from core.helper.model_serv import ModelLike
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from person.models import CofkUnionPerson
from tombstone.features.dataset import inst_features, person_features, location_features, work_features
from tombstone.models import TombstoneRequest
from tombstone.services import tombstone_schedule, tombstone
from tombstone.services.tombstone import IdsCluster
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


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


def render_cluster_results(request, clusters: list[WebClusterLike], template_name, merge_page_url=None,
                           is_running=False, last_update_at=None):
    return render(request, template_name,
                  {
                      'clusters': clusters,
                      'merge_page_url': merge_page_url,
                      'is_running': is_running,
                      'last_update_at': last_update_at,
                  })


def load_cluster_results(_create_id_records_dict, cluster_factory, model_name):
    record = TombstoneRequest.objects.filter(model_name=model_name).first()
    clusters = []
    last_update_at = None
    if record and record.result_jsonl:
        clusters = record.result_jsonl.split('\n')
        clusters = (json.loads(cluster) for cluster in clusters)
        clusters = (IdsCluster(ids=cluster['ids'], distance=cluster['distance'])
                    for cluster in clusters)
        clusters = build_display_clusters(clusters, cluster_factory, _create_id_records_dict)
        last_update_at = record.change_timestamp
    return clusters, last_update_at


def home(request):
    return render(request, 'tombstone/tombstone_basic.html')


@permission_required(constant.PM_TOMBSTONE_WORK)
def similar_work(request):
    def _create_id_records_dict(ids):
        return {r.iwork_id: r for r in CofkUnionWork.objects.filter(iwork_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, WebCluster, CofkUnionWork.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_work.html',
                                  merge_page_url=(reverse('work:merge')),
                                  is_running=tombstone_schedule.work_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


@permission_required(constant.PM_TOMBSTONE_LOCATION)
def similar_location(request):
    def _create_id_records_dict(ids):
        return {r.location_id: r for r in CofkUnionLocation.objects.filter(location_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, LocationWebCluster,
                                                    CofkUnionLocation.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_location.html',
                                  merge_page_url=(reverse('location:merge')),
                                  is_running=tombstone_schedule.location_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


@permission_required(constant.PM_TOMBSTONE_PERSON)
def similar_person(request):
    def _create_id_records_dict(ids):
        return {r.iperson_id: r for r in CofkUnionPerson.objects.filter(iperson_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, PersonWebCluster,
                                                    CofkUnionPerson.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_person.html',
                                  merge_page_url=(reverse('person:merge')),
                                  is_running=tombstone_schedule.person_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)



@permission_required(constant.PM_TOMBSTONE_INST)
def similar_inst(request):
    def _create_id_records_dict(ids):
        return {r.institution_id: r for r in CofkUnionInstitution.objects.filter(institution_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, InstWebCluster,
                                                    CofkUnionInstitution.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_inst.html',
                                  merge_page_url=(reverse('institution:merge')),
                                  is_running=tombstone_schedule.inst_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


@require_POST
@permission_required(constant.PM_TOMBSTONE_WORK)
def trigger_work_clustering(request):
    queryset = CofkUnionWork.objects.filter().values(*work_features.REQUIRED_FIELDS)
    tombstone.trigger_clustering(CofkUnionWork.__name__, queryset,
                                 tombstone_schedule.work_status_handler,
                                 username=request.user.username)
    return redirect('tombstone:work')


@require_POST
@permission_required(constant.PM_TOMBSTONE_LOCATION)
def trigger_location_clustering(request):
    queryset = CofkUnionLocation.objects.filter().values(*location_features.REQUIRED_FIELDS)
    tombstone.trigger_clustering(CofkUnionLocation.__name__, queryset,
                                 tombstone_schedule.location_status_handler,
                                 username=request.user.username)
    return redirect('tombstone:location')


@require_POST
@permission_required(constant.PM_TOMBSTONE_PERSON)
def trigger_person_clustering(request):
    queryset = CofkUnionPerson.objects.filter().values(*person_features.REQUIRED_FIELDS)
    tombstone.trigger_clustering(CofkUnionPerson.__name__, queryset,
                                 tombstone_schedule.person_status_handler,
                                 username=request.user.username)
    return redirect('tombstone:person')


@require_POST
@permission_required(constant.PM_TOMBSTONE_INST)
def trigger_inst_clustering(request):
    queryset = CofkUnionInstitution.objects.filter().values(*inst_features.REQUIRED_FIELDS)
    tombstone.trigger_clustering(CofkUnionInstitution.__name__, queryset,
                                 tombstone_schedule.inst_status_handler,
                                 username=request.user.username)
    return redirect('tombstone:inst')
