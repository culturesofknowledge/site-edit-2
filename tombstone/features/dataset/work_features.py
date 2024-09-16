import logging
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer

from tombstone.features import feature_utils

log = logging.getLogger(__name__)


def prepare_raw_df(records: Iterable) -> pd.DataFrame:
    field_extractors = {
        'description': lambda r: feature_utils.get_str_or_random(r, 'description', 200),
        'abstract': lambda r: feature_utils.get_str_or_random(r, 'abstract', 200),
        'authors_as_marked': lambda r: feature_utils.get_str_or_random(r, 'authors_as_marked', 100),
        'addressees_as_marked': lambda r: feature_utils.get_str_or_random(r, 'addressees_as_marked', 100),
        'origin_as_marked': lambda r: feature_utils.get_str_or_random(r, 'origin_as_marked', 50),
        'keywords': lambda r: feature_utils.get_str_or_random(r, 'keywords', 100),
        'incipit': lambda r: feature_utils.get_str_or_random(r, 'incipit', 100),
        'accession_code': lambda r: feature_utils.get_str_or_random(r, 'accession_code', 80),
    }
    record_df = feature_utils.build_raw_df(field_extractors, [r.iwork_id for r in records], records)
    return record_df


def create_features(work_raw_df: pd.DataFrame):
    preprocessor = ColumnTransformer(
        transformers=[
            ('description', feature_utils.create_text_pipeline(30), 'description'),
            ('abstract', feature_utils.create_text_pipeline(15), 'abstract'),
            ('authors_as_marked', feature_utils.create_text_pipeline(3), 'authors_as_marked'),
            ('addressees_as_marked', feature_utils.create_text_pipeline(3), 'addressees_as_marked'),
            ('keywords', feature_utils.create_text_pipeline(1), 'keywords'),
            ('incipit', feature_utils.create_text_pipeline(1), 'incipit'),
        ]
    )
    features = preprocessor.fit_transform(work_raw_df)
    return features
