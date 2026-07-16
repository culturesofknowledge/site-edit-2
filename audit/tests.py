from django.test import TestCase

from audit.models import CofkUnionAuditLiteral
from audit.views import find_merge_target
from core.models import MergeHistory


class MergeTargetTests(TestCase):
    """A deleted person/location/institution record's audit row should point
    at where it was merged to, using the MergeHistory row recorded when the
    merge happened (see core.helper.view_serv.MergeActionViews.merge)."""

    def test_find_merge_target_matches_person_delete_by_key_value_text(self):
        MergeHistory.objects.create(
            new_id='person_winner', new_name='Winner Name', new_display_id='123',
            old_id='person_loser', old_name='Loser Name', old_display_id='456',
            model_class_name='CofkUnionPerson',
            creation_user='tester', change_user='tester',
        )
        record = CofkUnionAuditLiteral(
            change_user='tester', change_type='Del', table_name='cofk_union_person',
            key_value_text='person_loser', key_value_integer=456,
            column_name='person_id',
        )

        merge_history = find_merge_target(record)

        self.assertIsNotNone(merge_history)
        self.assertEqual(merge_history.new_name, 'Winner Name')
        self.assertEqual(merge_history.new_display_id, '123')

    def test_find_merge_target_returns_none_for_non_delete(self):
        record = CofkUnionAuditLiteral(
            change_user='tester', change_type='Upd', table_name='cofk_union_person',
            key_value_text='person_loser', column_name='foaf_name',
        )

        self.assertIsNone(find_merge_target(record))

    def test_find_merge_target_returns_none_for_non_mergeable_table(self):
        record = CofkUnionAuditLiteral(
            change_user='tester', change_type='Del', table_name='cofk_union_work',
            key_value_text='work_1', column_name='work_id',
        )

        self.assertIsNone(find_merge_target(record))

    def test_find_merge_target_returns_none_when_no_merge_history(self):
        record = CofkUnionAuditLiteral(
            change_user='tester', change_type='Del', table_name='cofk_union_person',
            key_value_text='someone_never_merged', column_name='person_id',
        )

        self.assertIsNone(find_merge_target(record))
