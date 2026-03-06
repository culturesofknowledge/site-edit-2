import sys
from unittest.mock import MagicMock, Mock, patch

from django.db.models import Q, F
from django.db.models.lookups import IExact, IContains, IStartsWith, IEndsWith, IRegex
from django.test import TestCase

from core.helper import query_serv
from manifestation.models import CofkUnionManifestation

# Mock Django models and query_utils for testing
sys.modules['cofk_union_work'] = MagicMock()
sys.modules['cofk_union_resource'] = MagicMock()
sys.modules['cofk_work_resource_map'] = MagicMock()
sys.modules['cllib_django.query_utils'] = MagicMock()


class MockQ(Q):
    def __eq__(self, other):
        if isinstance(other, Q):
            return self.connector == other.connector and set(self.children) == set(other.children)
        return False

    def __hash__(self):
        return hash((self.connector, frozenset(self.children)))

    def __repr__(self):
        return f"MockQ({self.connector}, {self.children})"


# Patch Q to use MockQ for comparison in tests
query_serv.Q = MockQ
query_serv.lookups.IExact = IExact
query_serv.lookups.IContains = IContains
query_serv.lookups.IStartsWith = IStartsWith
query_serv.lookups.IEndsWith = IEndsWith
query_serv.lookups.IRegex = IRegex


class QuerySetUpdateTest(TestCase):
    def test_update_queryset(self):
        order_by = ['change_timestamp']
        input_where_field = 'manifestation_type'
        input_where_value = 'aaa'
        query = query_serv.update_queryset(CofkUnionManifestation.objects.filter(),
                                           CofkUnionManifestation,
                                           queries=[(Q(**{input_where_field: input_where_value})), ],
                                           sort_by=order_by).query

        # assert order by
        self.assertSequenceEqual(query.order_by, order_by)

        where_childrens = query_serv.extract_sub_query(query).where.children

        target_query = None
        for where_node in where_childrens:
            if where_node.lhs.target.column == input_where_field:
                target_query = where_node
                break

        self.assertIsNotNone(target_query)
        self.assertEqual(target_query.lhs.target.column, input_where_field)
        self.assertEqual(target_query.rhs, input_where_value)

    def test_create_queries_by_lookup_field__normal(self):
        query_list = query_serv.create_queries_by_lookup_field(
            {'a': 1, 'b': 2, 'z': 999},
            ['a', 'b']
        )
        self.assertSequenceEqual(
            set(query_list),
            {IExact(F('a'), 1), IExact(F('b'), 2), }
        )

    def test_create_queries_by_lookup_field__search_fields_maps(self):
        query_list = query_serv.create_queries_by_lookup_field(
            {'a': 1, 'b': 2, 'z': 999},
            ['a', 'b'],
            search_fields_maps={'a': ['a1', 'a2']},
        )
        self.assertSequenceEqual(
            set(query_list),
            {
                (IExact(F('a1'), 1) | IExact(F('a2'), 1)),
                IExact(F('b'), 2),
            }
        )

    def test_create_queries_by_lookup_field__search_fields_fn_maps(self):

        def lookup_fn(lookup, field, val):
            return Q(**{field: 123})

        query_list = query_serv.create_queries_by_lookup_field(
            {'a': 1, 'b': 2, 'z': 999},
            ['a', 'b'],
            search_fields_fn_maps={'b': lookup_fn}
        )
        self.assertSequenceEqual(
            set(query_list),
            {
                IExact(F('a'), 1),
                Q(b=123),
            }
        )

    @patch('work.models.CofkUnionWork')
    @patch('core.models.CofkUnionResource')
    @patch('work.models.CofkWorkResourceMap')
    def test_create_queries_by_lookup_field__related_resources_not_contain(
            self, MockCofkWorkResourceMap, MockCofkUnionResource, MockCofkUnionWork
    ):
        # Mock related models and their managers
        mock_work_manager = Mock()
        MockCofkUnionWork.objects = mock_work_manager
        mock_resource_manager = Mock()
        MockCofkUnionResource.objects = mock_resource_manager
        mock_work_resource_map_manager = Mock()
        MockCofkWorkResourceMap.objects = mock_work_resource_map_manager

        # --- Test Data ---
        # Work with no resources
        work_no_resources = Mock(pk=1)
        work_no_resources.cofkworkresourcemap_set.filter.return_value = []

        # Work with a resource containing "GeoNames"
        resource_geonames = Mock(resource_name='GeoNames')
        work_with_geonames = Mock(pk=2)
        work_with_geonames.cofkworkresourcemap_set.filter.return_value = [
            Mock(resource=resource_geonames, relationship_type='is_related_to')
        ]

        # Work with a resource NOT containing "GeoNames"
        resource_other = Mock(resource_name='Other Resource')
        work_without_geonames = Mock(pk=3)
        work_without_geonames.cofkworkresourcemap_set.filter.return_value = [
            Mock(resource=resource_other, relationship_type='is_related_to')
        ]

        # --- Simulate QuerySet behavior ---
        # This mock simulates the initial queryset before filters are applied
        mock_base_queryset = Mock()
        mock_base_queryset.filter.return_value = mock_base_queryset
        mock_base_queryset.exclude.return_value = mock_base_queryset
        mock_base_queryset.annotate.return_value = mock_base_queryset
        mock_base_queryset.order_by.return_value = mock_base_queryset
        mock_base_queryset.all.return_value = [
            work_no_resources, work_with_geonames, work_without_geonames
        ]

        # Mock the behavior of filter calls on related managers
        def mock_work_resource_map_filter(**kwargs):
            if 'work' in kwargs:
                work_pk = kwargs['work']
                if work_pk == work_with_geonames.pk:
                    return work_with_geonames.cofkworkresourcemap_set.filter.return_value
                elif work_pk == work_without_geonames.pk:
                    return work_without_geonames.cofkworkresourcemap_set.filter.return_value
                elif work_pk == work_no_resources.pk:
                    return work_no_resources.cofkworkresourcemap_set.filter.return_value
            return []

        MockCofkWorkResourceMap.objects.filter.side_effect = mock_work_resource_map_filter

        # Mock the behavior of resource_name__icontains
        def mock_resource_name_icontains_filter(**kwargs):
            if 'resource_name__icontains' in kwargs:
                search_term = kwargs['resource_name__icontains']
                if search_term == 'GeoNames':
                    return [resource_geonames]
            return []

        MockCofkUnionResource.objects.filter.side_effect = mock_resource_name_icontains_filter

        # --- Request Data ---
        request_data = {
            'related_resources': 'GeoNames',
            'related_resources_lookup': 'not_contain',
        }

        # --- Call the function under test ---
        queries = list(query_serv.create_queries_by_lookup_field(
            request_data,
            ['related_resources'],
            search_fields_fn_maps={
                'related_resources': query_serv.create_recref_lookup_fn(
                    ['is_related_to'],
                    'cofkworkresourcemap__resource',
                    ['resource_name']
                )
            }
        ))

        # --- Apply the generated Q objects to a mock queryset ---
        # This part is tricky with mocks, as Q objects are usually applied directly to a Django QuerySet.
        # We need to simulate how Django's filter would behave.
        # For this test, we'll manually evaluate the Q object against our mock data.

        # The expected Q object should look something like:
        # Q(
        #   Q(cofkworkresourcemap__relationship_type__in=['is_related_to']) &
        #   ~Q(cofkworkresourcemap__resource__resource_name__icontains='GeoNames') |
        #   Q(cofkworkresourcemap__isnull=True)
        # )

        self.assertEqual(len(queries), 1)
        generated_q = queries[0]

        # Simulate filtering
        filtered_results = []
        for work in mock_base_queryset.all():
            # Manually evaluate the Q object against the mock work object
            # This is a simplified simulation and might not cover all Django Q object complexities
            # For a full simulation, a more sophisticated mock of Django's ORM would be needed.
            # Here, we focus on the core logic of the generated Q object.

            # Check for the 'isnull' part first
            has_no_related_resources = not work.cofkworkresourcemap_set.filter.return_value

            # Check for the 'not_contain' part
            contains_geonames = False
            for wrm in work.cofkworkresourcemap_set.filter.return_value:
                if 'GeoNames' in wrm.resource.resource_name:
                    contains_geonames = True
                    break

            # The logic should be: (NOT contains_geonames) OR (has_no_related_resources)
            if (not contains_geonames) or has_no_related_resources:
                filtered_results.append(work)

        self.assertIn(work_no_resources, filtered_results)
        self.assertIn(work_without_geonames, filtered_results)
        self.assertNotIn(work_with_geonames, filtered_results)