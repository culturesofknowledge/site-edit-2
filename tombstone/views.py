import dataclasses
import itertools
import logging

from django.shortcuts import render
from django.urls import reverse

from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from person.models import CofkUnionPerson
from tombstone.features.dataset import work_features, location_features, person_features, inst_features
from tombstone.services import tombstone
from tombstone.services.tombstone import IdsCluster
from work.models import CofkUnionWork

log = logging.getLogger(__name__)

N_TOP_CLUSTERS = 100


@dataclasses.dataclass
class WebCluster:
    records: list
    distance: float


@dataclasses.dataclass
class LocationWebCluster(WebCluster):
    @property
    def merge_ids(self):
        return [r.location_id for r in self.records]


def find_clusters(raw_df, feature_maker,
                  n_top_clusters=N_TOP_CLUSTERS,
                  score_threshold=0.5):
    feature_ids = raw_df.index.to_numpy()
    features = feature_maker(raw_df)
    clusters = tombstone.find_similar_clusters(features, feature_ids,
                                               score_threshold=score_threshold)[:n_top_clusters]
    return clusters


def build_display_clusters(clusters: list[IdsCluster], cluster_factory, create_id_records_dict):
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
    return render(request, template_name,
                  {
                      'clusters': clusters,
                      'merge_page_url': merge_page_url,
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
                                    'tombstone/tombstone_location.html', merge_page_url=reverse('location:merge'))


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
                                    score_threshold=score_threshold, )


def similar_inst(request):
    def _create_id_records_dict(ids):
        return {r.institution_id: r for r in CofkUnionInstitution.objects.filter(institution_id__in=ids)}

    records = CofkUnionInstitution.objects.all().values(
        *(
            'institution_id',
            'institution_name',
            'institution_synonyms',
            'institution_city',
            'institution_country',
        ),
    )
    raw_df = inst_features.prepare_raw_df(records)
    return render_tombstone_cluster(request, raw_df, inst_features.create_features, _create_id_records_dict,
                                    'tombstone/tombstone_inst.html', merge_page_url=reverse('institution:merge'))
