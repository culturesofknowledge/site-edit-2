import logging
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer

from tombstone.features import feature_utils

log = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    'iwork_id', 'pk',
    'description',
    'abstract',
    'authors_as_marked',
    'addressees_as_marked',
    'origin_as_marked',
    'keywords',
    'incipit',
    'accession_code',
]

FIELD_EXTRACTORS = {
    'mixed_field': lambda r: feature_utils.get_multi_str_or_random(r, [
        'description',
        'abstract',
        'authors_as_marked',
        'addressees_as_marked',
        'origin_as_marked',
        'keywords',
        'incipit',
        'accession_code',
    ]),
}


def prepare_raw_df(records: Iterable[dict]) -> pd.DataFrame:
    record_df = feature_utils.build_raw_df(FIELD_EXTRACTORS, [r['iwork_id'] for r in records], records)
    return record_df


def create_features(work_raw_df: pd.DataFrame):
    preprocessor = ColumnTransformer(
        transformers=[
            ('mixed_field', feature_utils.create_text_pipeline(
                n_output_features=feature_utils.get_pca_n_components(100, work_raw_df.shape[0]),
                max_features=10000), 'mixed_field'),
        ])
    features = preprocessor.fit_transform(work_raw_df)
    return features
