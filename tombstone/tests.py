# Create your tests here.
import datetime
from typing import Callable

import numpy as np
import pandas as pd
from django.test import TestCase

from tombstone.features.dataset import inst_features, work_features, person_features, location_features
from tombstone.services import tombstone

records_inst = [
    {'institution_id': 1, 'institution_name': 'Apple', 'institution_synonyms': 'syn1',
     'institution_city': 'city1', 'institution_country': 'country1'},
    {'institution_id': 2, 'institution_name': 'Apple', 'institution_synonyms': 'syn2',
     'institution_city': 'city2', 'institution_coGuntry': 'country2'},
    {'institution_id': 3, 'institution_name': 'Store', 'institution_synonyms': 'syn3',
     'institution_city': 'city3', 'institution_country': 'country3'},
    {'institution_id': 4, 'institution_name': 'Sun', 'institution_synonyms': 'syn4',
     'institution_city': 'city4', 'institution_country': 'country4'},
]

records_work = [
    {'iwork_id': 1, 'description': 'Apple', 'abstract': 'abs1', 'authors_as_marked': 'auth1',
     'addressees_as_marked': 'addr1', 'origin_as_marked': 'origin1', 'keywords': 'key1',
     'incipit': 'inci1', 'accession_code': 'acc1'},
    {'iwork_id': 2, 'description': 'Store', 'abstract': 'abs2', 'authors_as_marked': 'auth2',
     'addressees_as_marked': 'addr2', 'origin_as_marked': 'origin2', 'keywords': 'key2',
     'incipit': 'inci2', 'accession_code': 'acc2'},
    {'iwork_id': 3, 'description': 'Store', 'abstract': 'abs3', 'authors_as_marked': 'auth3',
     'addressees_as_marked': 'addr3', 'origin_as_marked': 'origin3', 'keywords': 'key3',
     'incipit': 'inci3', 'accession_code': 'acc3'},
    {'iwork_id': 4, 'description': 'Apple', 'abstract': 'abs4', 'authors_as_marked': 'auth4',
     'addressees_as_marked': 'addr4', 'origin_as_marked': 'origin4', 'keywords': 'key4',
     'incipit': 'inci4', 'accession_code': 'acc4'},
]

records_person = [
    {'iperson_id': 1, 'foaf_name': 'Apple', 'skos_altlabel': 'alt1',
     'date_of_birth': datetime.datetime.strptime('2000-01-01', '%Y-%m-%d').date()},
    {'iperson_id': 2, 'foaf_name': 'Store', 'skos_altlabel': 'alt2',
     'date_of_birth': datetime.datetime.strptime('2000-01-02', '%Y-%m-%d').date()},
    {'iperson_id': 3, 'foaf_name': 'Sun', 'skos_altlabel': 'alt3',
     'date_of_birth': datetime.datetime.strptime('2000-01-03', '%Y-%m-%d').date()},
    {'iperson_id': 4, 'foaf_name': 'Sun', 'skos_altlabel': 'alt4',
     'date_of_birth': datetime.datetime.strptime('2000-01-04', '%Y-%m-%d').date()},
]

records_location = [
    {'location_id': 1, 'location_name': 'Apple', 'latitude': 1.1, 'longitude': 1.2},
    {'location_id': 2, 'location_name': 'Store', 'latitude': 2.1, 'longitude': 2.2},
    {'location_id': 3, 'location_name': 'Store', 'latitude': 3.1, 'longitude': 3.2},
    {'location_id': 4, 'location_name': 'Sun', 'latitude': 4.1, 'longitude': 4.2},
]


def assert_create_features(records, prepare_raw_df, create_features):
    raw_df = prepare_raw_df(records)
    features = create_features(raw_df)
    assert isinstance(features, np.ndarray)
    assert features.shape[0] == len(records_inst)


class ClusteringTestingTools:
    def __init__(self, records: list[dict], prepare_raw_df: Callable, create_features: Callable):
        self.records = records
        self.prepare_raw_df = prepare_raw_df
        self.create_features = create_features

    def _to_py_ids(self, cluster_ids):
        return {int(i) for i in cluster_ids}

    def test_create_clusters(self, first_cluster_ids):
        raw_df = self.prepare_raw_df(records_inst)
        clusters = tombstone.create_clusters(raw_df, self.create_features)
        assert self._to_py_ids(clusters[0].ids) == set(first_cluster_ids)

    def test_create_features(self):
        raw_df = self.prepare_raw_df(self.records)
        features = self.create_features(raw_df)
        assert isinstance(features, np.ndarray)
        assert features.shape[0] == len(records_inst)

    def assert_prepare_raw(self, raw_df, n_col, id_field):
        assert isinstance(raw_df, pd.DataFrame)
        assert raw_df.shape == (len(records_inst), n_col)
        assert raw_df.index.tolist() == [int(r[id_field]) for r in records_inst]


class TestInstClustering(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testing_tools = ClusteringTestingTools(records_inst, inst_features.prepare_raw_df,
                                                   inst_features.create_features)

    def test_prepare_raw(self):
        raw_df = self.testing_tools.prepare_raw_df(records_inst)
        self.testing_tools.assert_prepare_raw(raw_df, 3, 'institution_id')
        assert raw_df.loc[1, 'mixed_field'] == 'Apple syn1'

    def test_create_features(self):
        self.testing_tools.test_create_features()

    def test_create_clusters(self):
        self.testing_tools.test_create_clusters({1, 2})


class TestWorkFeatures(TestCase):
    def test_prepare_raw(self):
        raw_df = work_features.prepare_raw_df(records_work)
        assert isinstance(raw_df, pd.DataFrame)
        assert raw_df.shape == (len(records_inst), 1)
        assert raw_df.index.tolist() == [1, 2, 3, 4]
        assert raw_df.loc[1, 'mixed_field'] == 'Apple abs1 auth1 addr1 origin1 key1 inci1 acc1'

    def test_create_features(self):
        assert_create_features(records_work, work_features.prepare_raw_df, work_features.create_features)


class TestPersonFeatures(TestCase):
    def test_prepare_raw(self):
        raw_df = person_features.prepare_raw_df(records_person)
        assert isinstance(raw_df, pd.DataFrame)
        assert raw_df.shape == (len(records_person), 3)
        assert raw_df.index.tolist() == [1, 2, 3, 4]
        assert raw_df.loc[1, 'mixed_field'] == 'Apple alt1'

    def test_create_features(self):
        assert_create_features(records_person, person_features.prepare_raw_df, person_features.create_features)


class TestLocationFeatures(TestCase):
    def test_prepare_raw(self):
        raw_df = location_features.prepare_raw_df(records_location)
        assert isinstance(raw_df, pd.DataFrame)
        assert raw_df.shape == (len(records_location), 3)
        assert raw_df.index.tolist() == [1, 2, 3, 4]
        assert raw_df.loc[1, 'location_name'] == 'Apple'

    def test_create_features(self):
        assert_create_features(records_location, location_features.prepare_raw_df, location_features.create_features)
