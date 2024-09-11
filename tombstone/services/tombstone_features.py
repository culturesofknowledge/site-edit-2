import logging
import random
import string

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from work.models import CofkUnionWork

log = logging.getLogger(__name__)


def create_random_str(size=100, seed=42):
    s = string.ascii_letters + string.digits
    random.seed(seed)
    return ''.join(random.choices(s, k=size))


def _get_str(record, field_name, max_len=None):
    default_str_len = max_len or 100
    default_value = create_random_str(size=default_str_len)
    val = getattr(record, field_name, default_value) or default_value
    if max_len:
        val = val[:max_len]
    return val


def prepare_work_raw_df(works=None):
    log.info('Loading data')

    if works is None:
        works = CofkUnionWork.objects.all()

    field_extractors = {
        'description': lambda r: _get_str(r, 'description', 200),
        'abstract': lambda r: _get_str(r, 'abstract', 100),
    }

    record_df = pd.DataFrame([
        {
            field: field_extractor(r)
            for field, field_extractor in field_extractors.items()
        } for r in works
    ], index=[r.iwork_id for r in works])

    return record_df


def create_features(work_raw_df):
    log.info('Preprocessing data')
    text_transformer = TfidfVectorizer()
    preprocessor = ColumnTransformer(
        transformers=[
            ('text_description', text_transformer, 'description'),
            ('text_abstract', text_transformer, 'abstract'),
        ]
    )
    X = preprocessor.fit_transform(work_raw_df)
    return X
