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
from tombstone.models import TombstoneRequest
from tombstone.services import tombstone_schedule
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


def trigger_clustering(request, model_name, queryset, status_handler, redirect_to):
    task = TombstoneRequest.objects.filter(model_name=model_name).first()
    if not task:
        task = TombstoneRequest(model_name=model_name)
        task.update_current_user_timestamp(request.user.username)
    task.sql = str(queryset.query)
    task.save()
    status_handler.mark_pending()
    if not tombstone_schedule.status_handler.is_pending_or_running():
        tombstone_schedule.status_handler.mark_pending()

    return redirect(redirect_to)


def home(request):
    return render(request, 'tombstone/tombstone_basic.html')


def similar_work(request):
    def _create_id_records_dict(ids):
        return {r.iwork_id: r for r in CofkUnionWork.objects.filter(iwork_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, WebCluster, CofkUnionWork.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_work.html',
                                  merge_page_url=(reverse('work:merge')),
                                  is_running=tombstone_schedule.work_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


def similar_location(request):
    def _create_id_records_dict(ids):
        return {r.location_id: r for r in CofkUnionLocation.objects.filter(location_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, LocationWebCluster,
                                                     CofkUnionLocation.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_location.html',
                                  merge_page_url=(reverse('location:merge')),
                                  is_running=tombstone_schedule.location_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


def similar_person(request):
    def _create_id_records_dict(ids):
        return {r.iperson_id: r for r in CofkUnionPerson.objects.filter(iperson_id__in=ids)}

    clusters, last_update_at = load_cluster_results(_create_id_records_dict, PersonWebCluster,
                                                    CofkUnionPerson.__name__)
    return render_cluster_results(request, clusters, 'tombstone/tombstone_person.html',
                                  merge_page_url=(reverse('person:merge')),
                                  is_running=tombstone_schedule.person_status_handler.is_pending_or_running(),
                                  last_update_at=last_update_at)


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
def trigger_work_clustering(request):
    return trigger_clustering(request,
                              CofkUnionWork.__name__,
                              CofkUnionWork.objects.filter().values(*tombstone_schedule.WORK_FIELDS),
                              tombstone_schedule.work_status_handler,
                              'tombstone:work')


@require_POST
def trigger_location_clustering(request):
    return trigger_clustering(request,
                              CofkUnionLocation.__name__,
                              CofkUnionLocation.objects.filter().values(*tombstone_schedule.LOCATION_FIELDS),
                              tombstone_schedule.location_status_handler,
                              'tombstone:location')


@require_POST
def trigger_person_clustering(request):
    return trigger_clustering(request,
                              CofkUnionPerson.__name__,
                              CofkUnionPerson.objects.filter().values(*tombstone_schedule.PERSON_FIELDS),
                              tombstone_schedule.person_status_handler,
                              'tombstone:person')


@require_POST
def trigger_inst_clustering(request):
    return trigger_clustering(request,
                              CofkUnionInstitution.__name__,
                              CofkUnionInstitution.objects.filter().values(*tombstone_schedule.INST_FIELDS),
                              tombstone_schedule.inst_status_handler,
                              'tombstone:inst')
