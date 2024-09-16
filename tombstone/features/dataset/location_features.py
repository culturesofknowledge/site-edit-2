import logging
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler

from tombstone.features import feature_utils

log = logging.getLogger(__name__)


def prepare_raw_df(records: Iterable) -> pd.DataFrame:
    field_extractors = {
        'location_name': lambda r: feature_utils.get_str_or_random(r, 'location_name', 200),
        'location_synonyms': lambda r: feature_utils.get_str_or_random(r, 'location_synonyms', 80),
        'latitude': lambda r: feature_utils.get_float_or_random(r, 'latitude', 50),
        'longitude': lambda r: feature_utils.get_float_or_random(r, 'longitude', 50),
    }
    record_df = feature_utils.build_raw_df(field_extractors, [r.location_id for r in records], records)
    return record_df


def create_features(raw_df: pd.DataFrame):
    float_scaler = RobustScaler()
    preprocessor = ColumnTransformer(
        transformers=[
            ('location_name', feature_utils.create_text_pipeline(30), 'location_name'),
            ('location_synonyms', feature_utils.create_text_pipeline(5), 'location_synonyms'),
            ('latitude', float_scaler, ['latitude']),
            ('longitude', float_scaler, ['longitude']),
        ]
    )
    features = preprocessor.fit_transform(raw_df)
    return features
