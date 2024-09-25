import logging
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler

from tombstone.features import feature_utils

log = logging.getLogger(__name__)


FIELD_EXTRACTORS = {
    'location_name': lambda r: feature_utils.get_str_or_random(r, 'location_name', 200),
    'latitude': lambda r: feature_utils.get_float_or_random(r, 'latitude', 50),
    'longitude': lambda r: feature_utils.get_float_or_random(r, 'longitude', 50),
}

REQUIRED_FIELDS = [
    'location_id', 'pk',
] + list(FIELD_EXTRACTORS.keys())


def prepare_raw_df(records: Iterable[dict]) -> pd.DataFrame:
    record_df = feature_utils.build_raw_df(FIELD_EXTRACTORS, [r['location_id'] for r in records], records)
    return record_df


def create_features(raw_df: pd.DataFrame):
    float_scaler = RobustScaler()
    preprocessor = ColumnTransformer(
        transformers=[
            ('location_name', feature_utils.create_text_pipeline(None), 'location_name'),
            ('latitude', float_scaler, ['latitude']),
            ('longitude', float_scaler, ['longitude']),
        ]
    )
    features = preprocessor.fit_transform(raw_df)
    if not isinstance(features, np.ndarray):
        features = features.toarray()

    return features
