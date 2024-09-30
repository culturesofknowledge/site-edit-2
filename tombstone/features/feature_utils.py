import logging
import random
import string

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

log = logging.getLogger(__name__)


def create_random_str(size=100, seed=42):
    s = string.ascii_letters + string.digits
    random.seed(seed)
    return ''.join(random.choices(s, k=size))


def get_attr_value(record, field_name, default_value=None):
    if isinstance(record, dict):
        val = record.get(field_name, default_value)
    else:
        val = getattr(record, field_name, default_value)
    return val


def get_str_or_random(record: dict | object, field_name, max_len=None):
    default_str_len = max_len or 100
    default_value = create_random_str(size=default_str_len)
    val = get_attr_value(record, field_name, default_value)
    val = val or default_value
    if max_len:
        val = val[:max_len]
    return val


def get_multi_str_or_random(record: dict | object, field_names: list[str], max_len=None):
    default_str_len = max_len or 100
    default_value = create_random_str(size=default_str_len)

    vals = (get_attr_value(record, field_name, None)
            for field_name in field_names)
    vals = filter(None, vals)
    vals = ' '.join(vals)
    vals = vals or default_value
    return vals


def get_date_float_or_random(record, field_name):
    default_val = random.randint(620000, 720000)
    val = get_attr_value(record, field_name)
    if val:
        val = val.toordinal()
    else:
        val = default_val

    return val


def get_float_or_random(record, field_name, scale=1):
    default_value = random.random() * scale
    val = get_attr_value(record, field_name, default_value)
    if val is None:
        val = default_value
    try:
        val = float(val)
    except ValueError:
        val = default_value
    return val


def create_text_pipeline(n_output_features=None, max_features=None):
    steps = [
        ('tfidf', TfidfVectorizer(max_features=max_features)),
    ]
    if n_output_features:
        steps.append(('pca', PCA(n_components=n_output_features)))

    return Pipeline(steps)


def build_raw_df(field_extractors, index, works):
    record_df = pd.DataFrame([
        {
            field: field_extractor(r)
            for field, field_extractor in field_extractors.items()
        } for r in works
    ], index=index)
    return record_df


def get_pca_n_components(n_components, n_rows):
    return min(n_components, n_rows) - 1