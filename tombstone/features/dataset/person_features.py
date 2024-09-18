import logging
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler

from tombstone.features import feature_utils

log = logging.getLogger(__name__)

FIELD_EXTRACTORS = {
    'mixed_field': lambda r: feature_utils.get_multi_str_or_random(r, [
        'foaf_name',
        'skos_altlabel',
        # 'skos_hiddenlabel',
        # 'person_aliases'
    ]),
    'date_of_birth': lambda r: feature_utils.get_date_float_or_random(r, 'date_of_birth'),
    'date_of_death': lambda r: feature_utils.get_date_float_or_random(r, 'date_of_death'),
}


def prepare_raw_df(records: Iterable[dict]) -> pd.DataFrame:
    record_df = feature_utils.build_raw_df(FIELD_EXTRACTORS, [r['iperson_id'] for r in records], records)
    return record_df


def create_features(raw_df: pd.DataFrame):
    float_scaler = RobustScaler()
    preprocessor = ColumnTransformer(
        transformers=[
            ('mixed_field', feature_utils.create_text_pipeline(None, max_features=10000), 'mixed_field'),
            ('date_of_birth', float_scaler, ['date_of_birth']),
            ('date_of_death', float_scaler, ['date_of_death']),
        ]
    )

    features = preprocessor.fit_transform(raw_df)
    if not isinstance(features, np.ndarray):
        features = features.toarray()

    return features
