from django.db.models import Q, Exists
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
