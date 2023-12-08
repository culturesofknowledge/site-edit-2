from django.db.models import Q, Exists, F
from django.db.models.lookups import IExact
from django.test import TestCase

from core.helper import query_serv
from manifestation.models import CofkUnionManifestation


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

        # assert where clause
        lv1where_childrens = query.where.children
        self.assertEqual(len(lv1where_childrens), 1)
        self.assertIsInstance(lv1where_childrens[0].lhs, Exists)

        lv2where_childrens = lv1where_childrens[0].lhs.query.where.children
        self.assertGreater(len(lv2where_childrens), 1)

        target_query = None
        for where_node in lv2where_childrens:
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
                IExact(F('a1'), 1) | IExact(F('a2'), 1),
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
