import logging
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler

from clonefinder.features import feature_utils

log = logging.getLogger(__name__)

FIELD_EXTRACTORS = {
    'mixed_field': lambda r: feature_utils.get_multi_str_or_random(r, [
        'institution_name',
        'institution_synonyms',
    ]),
    'institution_city': lambda r: feature_utils.get_str_or_random(r, 'institution_city', 50),
    'institution_country': lambda r: feature_utils.get_str_or_random(r, 'institution_country', 50),
}

REQUIRED_FIELDS = (
    'institution_id',
    'institution_name',
    'institution_synonyms',
    'institution_city',
    'institution_country',
    'pk',
)


def prepare_raw_df(records: Iterable[dict]) -> pd.DataFrame:
    record_df = feature_utils.build_raw_df(FIELD_EXTRACTORS, [r['institution_id'] for r in records], records)
    return record_df


def create_features(raw_df: pd.DataFrame):
    float_scaler = RobustScaler()
    preprocessor = ColumnTransformer(
        transformers=[
            ('mixed_field', feature_utils.create_text_pipeline(max_features=10000), 'mixed_field'),
            ('institution_city', feature_utils.create_text_pipeline(max_features=100), 'institution_city'),
            ('institution_country', feature_utils.create_text_pipeline(max_features=100), 'institution_country'),
        ]
    )

    features = preprocessor.fit_transform(raw_df)
    if not isinstance(features, np.ndarray):
        features = features.toarray()

    return features
