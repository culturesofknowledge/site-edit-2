from django.test import TestCase

import person.fixtures
from audit.models import CofkUnionAuditLiteral
from audit.views import find_merge_target
from core import constant
from core.helper import test_serv
from core.models import CofkUnionRoleCategory, MergeHistory
from person.models import CofkPersonRoleMap


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


class PersonScalarFieldAuditTriggerTests(TestCase):
    """Gender and 'is organization' are plain columns on cofk_union_person
    (not Recref relationships), so they're audited by the Postgres trigger
    function dbf_cofk_union_audit_any (audit/trigger/dbf_cofk_union_audit_any_v4.sql)
    rather than by the Django signal handlers in audit/model_signals.py."""

    def _literals_for(self, pson, column_name, change_type):
        return CofkUnionAuditLiteral.objects.filter(
            table_name='cofk_union_person',
            key_value_integer=pson.iperson_id,
            column_name=column_name,
            change_type=change_type,
        )

    def test_creating_person_records_new_gender_and_is_organisation(self):
        pson = test_serv.create_person_by_dict(
            dict(person.fixtures.person_min_dict_a, gender='M', is_organisation='Y'))

        gender_literal = self._literals_for(pson, 'gender', constant.CHANGE_TYPE_NEW).first()
        self.assertIsNotNone(gender_literal)
        self.assertEqual(gender_literal.new_column_value, 'M')

        org_literal = self._literals_for(pson, 'is_organisation', constant.CHANGE_TYPE_NEW).first()
        self.assertIsNotNone(org_literal)
        self.assertEqual(org_literal.new_column_value, 'Y')

    def test_changing_gender_records_change_with_old_and_new_value(self):
        pson = test_serv.create_person_by_dict(
            dict(person.fixtures.person_min_dict_a, gender='M'))

        pson.gender = 'F'
        pson.save()

        literal = self._literals_for(pson, 'gender', constant.CHANGE_TYPE_CHANGE).first()
        self.assertIsNotNone(literal)
        self.assertEqual(literal.new_column_value, 'F')
        self.assertEqual(literal.old_column_value, 'M')

    def test_changing_is_organisation_records_change_with_old_and_new_value(self):
        pson = test_serv.create_person_by_dict(
            dict(person.fixtures.person_min_dict_a, is_organisation=''))

        pson.is_organisation = 'Y'
        pson.save()

        literal = self._literals_for(pson, 'is_organisation', constant.CHANGE_TYPE_CHANGE).first()
        self.assertIsNotNone(literal)
        self.assertEqual(literal.new_column_value, 'Y')
        self.assertEqual(literal.old_column_value, '')

    def test_saving_without_gender_change_does_not_record_spurious_change(self):
        pson = test_serv.create_person_by_dict(
            dict(person.fixtures.person_min_dict_a, gender='M'))

        pson.editors_notes = 'updated notes, gender untouched'
        pson.save()

        self.assertFalse(
            self._literals_for(pson, 'gender', constant.CHANGE_TYPE_CHANGE).exists())


class RecrefRelationAuditTests(TestCase):
    """Role categories, locations, related people, organizations etc. are
    all Recref subclasses: adding one should write a matching pair of
    audit records (one per side of the relationship) via
    model_signals.add_relation_audit_to_literal, and removing one should
    write a matching 'Del' pair via add_relation_audit_to_literal_on_delete.
    Role categories are used here as a representative Recref - every other
    relation type listed above shares the same _write_relation_audit_pair
    code path in audit/model_signals.py."""

    def _create_role_recref(self):
        pson = test_serv.create_person_by_dict(person.fixtures.person_min_dict_a)
        role = CofkUnionRoleCategory.objects.create(role_category_desc='Antiquary')
        recref = CofkPersonRoleMap(
            person=pson, role=role, relationship_type=constant.REL_TYPE_MEMBER_OF,
            creation_user='tester', change_user='tester',
        )
        recref.save()
        return recref

    def _relation_literals(self, recref_id, change_type):
        return CofkUnionAuditLiteral.objects.filter(
            key_value_integer=recref_id,
            change_type=change_type,
            column_name__startswith='Relationship: ',
        )

    def test_adding_role_records_two_new_relation_audit_records(self):
        recref = self._create_role_recref()

        literals = self._relation_literals(recref.recref_id, constant.CHANGE_TYPE_NEW)
        self.assertEqual(literals.count(), 2)
        self.assertEqual(
            {l.table_name for l in literals},
            {'cofk_union_person', 'cofk_union_role_category'})
        for literal in literals:
            self.assertTrue(literal.new_column_value)
            self.assertFalse(literal.old_column_value)

    def test_removing_role_records_two_del_relation_audit_records(self):
        recref = self._create_role_recref()
        recref_id = recref.recref_id

        recref.delete()

        literals = self._relation_literals(recref_id, constant.CHANGE_TYPE_DELETE)
        self.assertEqual(literals.count(), 2)
        self.assertEqual(
            {l.table_name for l in literals},
            {'cofk_union_person', 'cofk_union_role_category'})
        for literal in literals:
            self.assertTrue(literal.old_column_value)
            self.assertFalse(literal.new_column_value)
