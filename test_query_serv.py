import sys
from unittest.mock import MagicMock

# Mock Django
django_models = MagicMock()
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = django_models
sys.modules['django.db.models.lookups'] = MagicMock()
sys.modules['django.db.models.sql'] = MagicMock()
sys.modules['django.db.models.base'] = MagicMock()

# We need Q and F to be somewhat functional or at least identifiable
class MockQ:
    OR = 'OR'
    AND = 'AND'
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def __repr__(self):
        return f"Q({self.args}, {self.kwargs})"

django_models.Q = MockQ
django_models.F = MagicMock

# Mock cllib_django
sys.modules['cllib_django'] = MagicMock()
sys.modules['cllib_django.query_utils'] = MagicMock()

# Mock core.helper.date_serv and data_serv
sys.modules['core.helper.date_serv'] = MagicMock()
sys.modules['core.helper.data_serv'] = MagicMock()

# Mock more_itertools
sys.modules['more_itertools'] = MagicMock()

# Now we can import query_serv
import core.helper.query_serv as query_serv
query_serv.Q = MockQ

# Setup some mocks for query_utils
def mock_concat_queries(queries, conn_type=None):
    return ('CONCAT', list(queries), conn_type)

query_serv.query_utils.concat_queries = mock_concat_queries

def mock_run_lookup_fn(lookup_fn, field, val):
    return ('LOOKUP', lookup_fn, field, val)

query_serv.run_lookup_fn = mock_run_lookup_fn

# Test create_queries_by_lookup_field
def test_location_name_ends_with():
    request_data = {
        'location_name': 'England',
        'location_name_lookup': 'ends_with'
    }
    search_field_names = ['location_name']
    search_fields_maps = {'location_name': ['location_name', 'location_synonyms']}
    
    queries = list(query_serv.create_queries_by_lookup_field(
        request_data, search_field_names, search_fields_maps
    ))
    
    print(f"Queries: {queries}")
    
    # Expecting both fields to be searched
    assert len(queries) == 1
    concat_op, sub_queries, conn_type = queries[0]
    assert len(sub_queries) == 2
    assert sub_queries[0][2] == 'location_name'
    assert sub_queries[1][2] == 'location_synonyms'
    assert conn_type == 'OR'

def test_location_name_not_end_with():
    request_data = {
        'location_name': 'England',
        'location_name_lookup': 'not_end_with'
    }
    search_field_names = ['location_name']
    search_fields_maps = {'location_name': ['location_name', 'location_synonyms']}
    
    queries = list(query_serv.create_queries_by_lookup_field(
        request_data, search_field_names, search_fields_maps
    ))
    
    print(f"Queries: {queries}")
    
    # Expecting both fields to be searched with AND
    assert len(queries) == 1
    concat_op, sub_queries, conn_type = queries[0]
    assert len(sub_queries) == 2
    assert conn_type == 'AND'

def test_location_name_starts_with():
    request_data = {
        'location_name': 'London',
        'location_name_lookup': 'starts_with'
    }
    search_field_names = ['location_name']
    search_fields_maps = {'location_name': ['location_name', 'location_synonyms']}
    
    queries = list(query_serv.create_queries_by_lookup_field(
        request_data, search_field_names, search_fields_maps
    ))
    
    print(f"Queries: {queries}")
    
    # Expecting both fields to be searched
    assert len(queries) == 1
    concat_op, sub_queries, conn_type = queries[0]
    assert len(sub_queries) == 2
    assert sub_queries[0][2] == 'location_name'
    assert sub_queries[1][2] == 'location_synonyms'
    assert conn_type == 'OR'

if __name__ == '__main__':
    try:
        test_location_name_ends_with()
        print("test_location_name_ends_with passed!")
        test_location_name_not_end_with()
        print("test_location_name_not_end_with passed!")
        test_location_name_starts_with()
        print("test_location_name_starts_with passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)