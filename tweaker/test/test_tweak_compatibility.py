# -*- coding: utf-8 -*-
"""
Compatibility tests for tweak_* scripts.

These tests verify that the DatabaseTweaker can accomplish the same tasks
as the previous version in site-edit/emlo-edit-php-helper/tweaker,
using the new mapping table-based API.

Run with:
    python -m pytest tweaker/test/test_tweak_compatibility.py -v

Or with Django:
    python manage.py test tweaker.test.test_tweak_compatibility
"""
import os
import tempfile
import unittest
from unittest.mock import patch

# Try to import Django test classes - optional for unit tests
try:
    from django.test import TransactionTestCase
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    TransactionTestCase = unittest.TestCase
    DJANGO_AVAILABLE = False

# Try to import core constants
try:
    from core.constant import (
        REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM,
        REL_TYPE_WAS_SENT_TO, REL_TYPE_IS_RELATED_TO, REL_TYPE_MENTION,
        REL_TYPE_COMMENT_DATE, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_COMMENT_REFERS_TO,
        REL_TYPE_COMMENT_PERSON_MENTIONED, REL_TYPE_COMMENT_AUTHOR,
        REL_TYPE_WAS_BORN_IN_LOCATION, REL_TYPE_DIED_AT_LOCATION,
        REL_TYPE_WORK_IS_REPLY_TO,
    )
    CORE_AVAILABLE = True
except ImportError:
    REL_TYPE_CREATED = 'created'
    REL_TYPE_WAS_ADDRESSED_TO = 'was_addressed_to'
    REL_TYPE_WAS_SENT_FROM = 'was_sent_from'
    REL_TYPE_WAS_SENT_TO = 'was_sent_to'
    REL_TYPE_IS_RELATED_TO = 'is_related_to'
    REL_TYPE_MENTION = 'mentions'
    REL_TYPE_COMMENT_DATE = 'refers_to_date'
    REL_TYPE_COMMENT_ADDRESSEE = 'refers_to_addressee'
    REL_TYPE_COMMENT_REFERS_TO = 'refers_to'
    REL_TYPE_COMMENT_PERSON_MENTIONED = 'refers_to_people_mentioned_in_work'
    REL_TYPE_COMMENT_AUTHOR = 'refers_to_author'
    REL_TYPE_WAS_BORN_IN_LOCATION = 'was_born_in_location'
    REL_TYPE_DIED_AT_LOCATION = 'died_at_location'
    REL_TYPE_WORK_IS_REPLY_TO = 'is_reply_to'
    CORE_AVAILABLE = False


class TestTweakerMethodSignatures(unittest.TestCase):
    """
    Test that DatabaseTweaker has all the methods needed to accomplish
    the same tasks as the tweak_* scripts.
    """

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker()

    # === Core methods used by all scripts ===
    def test_class_has_tweaker_from_connection(self):
        from tweaker import DatabaseTweaker
        self.assertTrue(hasattr(DatabaseTweaker, 'tweaker_from_connection'))

    def test_has_set_debug(self):
        self.assertTrue(hasattr(self.dt, 'set_debug'))

    def test_has_get_csv_data(self):
        self.assertTrue(hasattr(self.dt, 'get_csv_data'))

    def test_has_print_audit(self):
        self.assertTrue(hasattr(self.dt, 'print_audit'))

    def test_has_commit_changes(self):
        self.assertTrue(hasattr(self.dt, 'commit_changes'))

    # === GET methods ===
    def test_has_get_work_from_iwork_id(self):
        """Used by: tweak_add_resources, tweak_template, tweak_huygens_manifestations"""
        self.assertTrue(hasattr(self.dt, 'get_work_from_iwork_id'))

    def test_has_get_work_from_work_id(self):
        self.assertTrue(hasattr(self.dt, 'get_work_from_work_id'))

    def test_has_get_manifestation_from_manifestation_id(self):
        """Used by: tweak_manifestations, tweak_work-delete"""
        self.assertTrue(hasattr(self.dt, 'get_manifestation_from_manifestation_id'))

    def test_has_get_resource_from_resource_id(self):
        """Used by: tweak_work-delete, tweak_resource-url"""
        self.assertTrue(hasattr(self.dt, 'get_resource_from_resource_id'))

    def test_has_get_person_from_person_id(self):
        self.assertTrue(hasattr(self.dt, 'get_person_from_person_id'))

    def test_has_get_person_from_iperson_id(self):
        """Used by: tweak_morris-add-note"""
        self.assertTrue(hasattr(self.dt, 'get_person_from_iperson_id'))

    def test_has_get_location_from_location_id(self):
        self.assertTrue(hasattr(self.dt, 'get_location_from_location_id'))

    def test_has_get_comment_from_comment_id(self):
        self.assertTrue(hasattr(self.dt, 'get_comment_from_comment_id'))

    def test_has_get_image_from_image_id(self):
        """Used by: tweak_images_broken"""
        self.assertTrue(hasattr(self.dt, 'get_image_from_image_id'))

    def test_has_get_institution_from_institution_id(self):
        self.assertTrue(hasattr(self.dt, 'get_institution_from_institution_id'))

    def test_has_get_languages_from_code(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'get_languages_from_code'))

    # === CREATE methods ===
    def test_has_create_resource(self):
        """Used by: tweak_add_resources, tweak_Morris2"""
        self.assertTrue(hasattr(self.dt, 'create_resource'))

    def test_has_create_comment(self):
        """Used by: tweak_morris-add-note, tweak_huygens_manifestations"""
        self.assertTrue(hasattr(self.dt, 'create_comment'))

    def test_has_create_person_or_organisation(self):
        """Used by: tweak_Morris2, tweak_MorrisPeople, tweak_people_gianmarco"""
        self.assertTrue(hasattr(self.dt, 'create_person_or_organisation'))

    def test_has_create_work(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_work'))

    def test_has_create_location(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_location'))

    def test_has_create_manifestation(self):
        """Used by: tweak_huygens_manifestations, tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_manifestation'))

    def test_has_create_image(self):
        self.assertTrue(hasattr(self.dt, 'create_image'))

    # === UPDATE methods ===
    def test_has_update_manifestation(self):
        """Used by: tweak_manifestations"""
        self.assertTrue(hasattr(self.dt, 'update_manifestation'))

    def test_has_update_work(self):
        """Used by: tweak_work_correct-editors-note"""
        self.assertTrue(hasattr(self.dt, 'update_work'))

    def test_has_update_person(self):
        """Used by: tweak_people_* scripts"""
        self.assertTrue(hasattr(self.dt, 'update_person'))

    def test_has_update_resource(self):
        """Used by: tweak_resource-url, tweak_resource-replace"""
        self.assertTrue(hasattr(self.dt, 'update_resource'))

    def test_has_update_location(self):
        self.assertTrue(hasattr(self.dt, 'update_location'))

    def test_has_update_comment(self):
        self.assertTrue(hasattr(self.dt, 'update_comment'))

    def test_has_update_image(self):
        """Used by: tweak_images_broken"""
        self.assertTrue(hasattr(self.dt, 'update_image'))

    # === DELETE methods ===
    def test_has_delete_work_via_iwork_id(self):
        """Used by: tweak_work-delete"""
        self.assertTrue(hasattr(self.dt, 'delete_work_via_iwork_id'))

    def test_has_delete_manifestation_via_manifestation_id(self):
        """Used by: tweak_work-delete"""
        self.assertTrue(hasattr(self.dt, 'delete_manifestation_via_manifestation_id'))

    def test_has_delete_resource_via_resource_id(self):
        """Used by: tweak_work-delete"""
        self.assertTrue(hasattr(self.dt, 'delete_resource_via_resource_id'))

    # === Mapping table CREATE methods ===
    def test_has_create_work_resource_map(self):
        self.assertTrue(hasattr(self.dt, 'create_work_resource_map'))

    def test_has_create_work_person_map(self):
        self.assertTrue(hasattr(self.dt, 'create_work_person_map'))

    def test_has_create_work_location_map(self):
        self.assertTrue(hasattr(self.dt, 'create_work_location_map'))

    def test_has_create_work_comment_map(self):
        self.assertTrue(hasattr(self.dt, 'create_work_comment_map'))

    def test_has_create_work_work_map(self):
        self.assertTrue(hasattr(self.dt, 'create_work_work_map'))

    def test_has_create_person_resource_map(self):
        self.assertTrue(hasattr(self.dt, 'create_person_resource_map'))

    def test_has_create_person_comment_map(self):
        self.assertTrue(hasattr(self.dt, 'create_person_comment_map'))

    def test_has_create_person_location_map(self):
        self.assertTrue(hasattr(self.dt, 'create_person_location_map'))

    def test_has_create_manif_inst_map(self):
        self.assertTrue(hasattr(self.dt, 'create_manif_inst_map'))

    def test_has_create_manif_comment_map(self):
        self.assertTrue(hasattr(self.dt, 'create_manif_comment_map'))

    # === Mapping table GET methods ===
    def test_has_get_work_resource_maps(self):
        self.assertTrue(hasattr(self.dt, 'get_work_resource_maps'))

    def test_has_get_work_person_maps(self):
        self.assertTrue(hasattr(self.dt, 'get_work_person_maps'))

    def test_has_get_work_location_maps(self):
        self.assertTrue(hasattr(self.dt, 'get_work_location_maps'))

    def test_has_get_work_comment_maps(self):
        self.assertTrue(hasattr(self.dt, 'get_work_comment_maps'))

    def test_has_get_work_work_maps(self):
        self.assertTrue(hasattr(self.dt, 'get_work_work_maps'))

    def test_has_get_manif_inst_maps(self):
        self.assertTrue(hasattr(self.dt, 'get_manif_inst_maps'))

    # === Mapping table DELETE methods ===
    def test_has_delete_work_resource_map(self):
        self.assertTrue(hasattr(self.dt, 'delete_work_resource_map'))

    def test_has_delete_work_person_map(self):
        self.assertTrue(hasattr(self.dt, 'delete_work_person_map'))

    def test_has_delete_work_location_map(self):
        self.assertTrue(hasattr(self.dt, 'delete_work_location_map'))

    def test_has_delete_work_comment_map(self):
        self.assertTrue(hasattr(self.dt, 'delete_work_comment_map'))

    # === Convenience relationship methods (work-person) ===
    def test_has_create_relationship_created(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_created'))

    def test_has_create_relationship_addressed_to(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_addressed_to'))

    def test_has_create_relationship_mentions(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_mentions'))

    # === Convenience relationship methods (work-location) ===
    def test_has_create_relationship_was_sent_from(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_was_sent_from'))

    def test_has_create_relationship_was_sent_to(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_was_sent_to'))

    def test_has_create_relationship_mentions_place(self):
        self.assertTrue(hasattr(self.dt, 'create_relationship_mentions_place'))

    # === Convenience relationship methods (work-resource) ===
    def test_has_create_relationship_work_resource(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_work_resource'))

    # === Convenience relationship methods (person-resource) ===
    def test_has_create_relationship_person_resource(self):
        """Used by: tweak_Morris2"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_person_resource'))

    # === Convenience relationship methods (work-comment / notes) ===
    def test_has_create_relationship_note_on_work_date(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_date'))

    def test_has_create_relationship_note_on_work_addressee(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_addressee'))

    def test_has_create_relationship_note_on_work_generally(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_generally'))

    def test_has_create_relationship_note_on_work_people_mentioned(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_people_mentioned'))

    def test_has_create_relationship_note_on_work_author(self):
        """Used by: tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_author'))

    def test_has_create_relationship_note_on_work_origin(self):
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_origin'))

    def test_has_create_relationship_note_on_work_destination(self):
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_destination'))

    def test_has_create_relationship_note_on_work_route(self):
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_work_route'))

    # === Convenience relationship methods (person-comment) ===
    def test_has_create_relationship_note_on_person(self):
        """Used by: tweak_morris-add-note"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_on_person'))

    # === Convenience relationship methods (manifestation) ===
    def test_has_create_relationship_manifestation_in_repository(self):
        """Used by: tweak_huygens_manifestations, tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_manifestation_in_repository'))

    def test_has_create_relationship_manifestation_of_work(self):
        """Used by: tweak_huygens_manifestations, tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_manifestation_of_work'))

    def test_has_create_relationship_note_manifestation(self):
        """Used by: tweak_huygens_manifestations, tweak_add_works_people_places_manifestations_repository"""
        self.assertTrue(hasattr(self.dt, 'create_relationship_note_manifestation'))

    # === Convenience relationship methods (work-work) ===
    def test_has_create_relationship_work_reply_to(self):
        self.assertTrue(hasattr(self.dt, 'create_relationship_work_reply_to'))

    def test_has_create_relationship_work_matches(self):
        self.assertTrue(hasattr(self.dt, 'create_relationship_work_matches'))


class TestCSVDataCompatibility(unittest.TestCase):
    """Test that CSV loading works correctly."""

    def test_get_csv_data_returns_list_of_dicts(self):
        from tweaker import DatabaseTweaker

        csv_content = "name,age,city\nAlice,30,London\nBob,25,Paris\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                         delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            rows = DatabaseTweaker.get_csv_data(temp_path)
            self.assertIsInstance(rows, list)
            self.assertEqual(len(rows), 2)
            self.assertIsInstance(rows[0], dict)
            self.assertEqual(rows[0]['name'], 'Alice')
        finally:
            os.unlink(temp_path)

    def test_get_csv_data_handles_unicode(self):
        from tweaker import DatabaseTweaker

        csv_content = "name,description\nTest,Müller über Größe\nAnother,日本語テスト\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                         delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            rows = DatabaseTweaker.get_csv_data(temp_path)
            self.assertIn('Müller', rows[0]['description'])
            self.assertIn('日本語', rows[1]['description'])
        finally:
            os.unlink(temp_path)


class TestAuditTracking(unittest.TestCase):
    """Test audit tracking functionality."""

    def test_audit_structure(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        self.assertIn('insertions', dt.audit)
        self.assertIn('updates', dt.audit)
        self.assertIn('deletions', dt.audit)

    def test_print_audit_does_not_crash(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        dt.print_audit()

    def test_audit_counts(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()

        dt._audit_insert("work")
        dt._audit_insert("work")
        dt._audit_update("person")
        dt._audit_delete("resource")

        self.assertEqual(dt.audit['insertions']['work'], 2)
        self.assertEqual(dt.audit['updates']['person'], 1)
        self.assertEqual(dt.audit['deletions']['resource'], 1)


class TestUtilityMethods(unittest.TestCase):
    """Test utility methods."""

    def test_get_int_value(self):
        from tweaker import DatabaseTweaker
        self.assertEqual(DatabaseTweaker.get_int_value(42), 42)
        self.assertEqual(DatabaseTweaker.get_int_value("123"), 123)
        self.assertIsNone(DatabaseTweaker.get_int_value(None))
        self.assertIsNone(DatabaseTweaker.get_int_value(""))
        self.assertEqual(DatabaseTweaker.get_int_value(None, 0), 0)

    def test_get_date_string(self):
        from tweaker import DatabaseTweaker
        self.assertEqual(DatabaseTweaker.get_date_string(2023, 5, 15), "2023-05-15")
        self.assertEqual(DatabaseTweaker.get_date_string(2023, None, None), "2023-12-31")
        self.assertEqual(DatabaseTweaker.get_date_string(2023, 2, None), "2023-02-28")
        self.assertEqual(DatabaseTweaker.get_date_string(None, None, None), "9999-12-31")

    def test_calendar_conversion(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()

        result = dt.calendar_julian_to_calendar_gregorian(15, 6, 1650)
        self.assertEqual(result, {'d': 25, 'm': 6, 'y': 1650})

        result = dt.calendar_julian_to_calendar_gregorian(25, 12, 1650)
        self.assertEqual(result, {'d': 4, 'm': 1, 'y': 1651})


class TestConnectionMethods(unittest.TestCase):
    """Test connection methods."""

    @patch.object(__import__('tweaker').DatabaseTweaker, 'connect')
    def test_tweaker_from_connection(self, mock_connect):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker.tweaker_from_connection(
            dbname='testdb', host='localhost', port='5432',
            user='testuser', password='testpass'
        )
        self.assertIsInstance(dt, DatabaseTweaker)

    @patch.object(__import__('tweaker').DatabaseTweaker, 'connect')
    def test_connect_to_postgres_legacy(self, mock_connect):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        dt.connect_to_postgres("dbname='testdb' host='localhost' port='5432' user='u' password='p'")
        mock_connect.assert_called_once()


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestTweakScriptIntegration(TransactionTestCase):
    """
    Integration tests verifying tweak_* script patterns work correctly.
    Each test corresponds to one or more actual tweak_* scripts.
    """

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    # === Pattern from tweak_add_resources.py ===
    def test_add_resources_to_work(self):
        """Get work, create resource, link to work."""
        work_id = self.dt.create_work(work_id_end="test_res", description="Test")
        resource_id = self.dt.create_resource("Test Resource", "https://example.com")

        recref_id = self.dt.create_work_resource_map(work_id, resource_id)
        self.assertIsNotNone(recref_id)

        maps = self.dt.get_work_resource_maps(work_id=work_id)
        self.assertEqual(len(maps), 1)

    # === Pattern from tweak_manifestations.py ===
    def test_update_manifestation(self):
        """Get manifestation, update fields."""
        work_id = self.dt.create_work(work_id_end="test_manif", description="Test")
        manif_id = self.dt.create_manifestation("test_manif_001", work_id=work_id, manifestation_type="ALS")

        self.dt.update_manifestation(manif_id, {"printed_edition_details": "Updated"})

        manif = self.dt.get_manifestation_from_manifestation_id(manif_id)
        self.assertEqual(manif['printed_edition_details'], "Updated")

    # === Pattern from tweak_work-delete.py ===
    def test_delete_work_with_relationships(self):
        """Create work with relationships, delete relationships, delete work."""
        work_id = self.dt.create_work(work_id_end="test_del", description="Test")
        resource_id = self.dt.create_resource("Delete test", "http://example.com")
        self.dt.create_work_resource_map(work_id, resource_id)

        work = self.dt.get_work_from_work_id(work_id)
        maps = self.dt.get_work_resource_maps(work_id=work_id)
        for m in maps:
            self.dt.delete_work_resource_map(m['recref_id'])

        self.dt.delete_work_via_iwork_id(work['iwork_id'])
        self.assertIsNone(self.dt.get_work_from_iwork_id(work['iwork_id']))

    # === Pattern from tweak_Morris2.py / tweak_MorrisPeople.py ===
    def test_create_person_with_resources(self):
        """Create person with full details, create resource, link."""
        person_id = self.dt.create_person_or_organisation(
            primary_name="Test Person",
            gender='M',
            birth_year=1800,
            death_year=1870,
            editors_notes="Test note"
        )
        resource_id = self.dt.create_resource("Person resource", "http://example.com")
        self.dt.create_person_resource_map(person_id, resource_id)

        person = self.dt.get_person_from_person_id(person_id)
        self.assertEqual(person['foaf_name'], "Test Person")

    # === Pattern from tweak_morris-add-note.py ===
    def test_add_note_to_person(self):
        """Get person by iperson_id, create comment, link to person."""
        person_id = self.dt.create_person_or_organisation(primary_name="Note Test Person")
        person = self.dt.get_person_from_person_id(person_id)

        # Get by iperson_id
        person2 = self.dt.get_person_from_iperson_id(person['iperson_id'])
        self.assertEqual(person2['person_id'], person_id)

        # Create and link comment
        comment_id = self.dt.create_comment("General note about person")
        self.dt.create_relationship_note_on_person(comment_id, person_id)

    # === Pattern from tweak_resource-url.py ===
    def test_update_resource_url(self):
        """Get resource, update URL."""
        resource_id = self.dt.create_resource("Test", "http://old-url.com")

        self.dt.update_resource(resource_id, {'resource_url': 'http://new-url.com'})

        resource = self.dt.get_resource_from_resource_id(resource_id)
        self.assertEqual(resource['resource_url'], 'http://new-url.com')

    # === Pattern from tweak_people_gianmarco.py ===
    def test_create_person_full_details(self):
        """Create person with birth/death/flourished details."""
        person_id = self.dt.create_person_or_organisation(
            primary_name="Gianmarco Test",
            synonyms="Alias Name",
            gender='M',
            is_org='',
            birth_year=1550,
            birth_inferred='Y',
            death_year=1620,
            flourished_year=1580,
            flourished2_year=1610,
            editors_notes="Test person"
        )

        person = self.dt.get_person_from_person_id(person_id)
        self.assertEqual(person['date_of_birth_year'], 1550)
        self.assertEqual(person['date_of_death_year'], 1620)

    # === Pattern from tweak_images_broken.py ===
    def test_update_image(self):
        """Get image, update thumbnail/licence_url."""
        image_id = self.dt.create_image(
            filename="test.jpg",
            display_order=1,
            image_credits="Test credits"
        )

        self.dt.update_image(image_id, {
            'thumbnail': 'http://new-thumbnail.com/thumb.jpg',
            'licence_url': 'http://new-licence.com'
        })

        image = self.dt.get_image_from_image_id(image_id)
        self.assertEqual(image['thumbnail'], 'http://new-thumbnail.com/thumb.jpg')

    # === Pattern from tweak_huygens_manifestations.py ===
    def test_create_manifestation_with_repository_and_notes(self):
        """Create manifestation, link to repository, link to work, add notes."""
        work_id = self.dt.create_work(work_id_end="test_huygens", description="Test")

        manif_id = self.dt.create_manifestation(
            "test_huygens_001",
            work_id=work_id,
            manifestation_type="ALS",
            id_number_or_shelfmark="MS 123"
        )

        # Link to work
        self.dt.create_relationship_manifestation_of_work(manif_id, work_id)

        # Add note
        comment_id = self.dt.create_comment("Manifestation note")
        self.dt.create_relationship_note_manifestation(comment_id, manif_id)

    # === Pattern from tweak_add_works_people_places_manifestations_repository.py ===
    def test_full_work_creation_workflow(self):
        """Create work with author, addressee, origin, destination, resources, notes."""
        # Create people
        author_id = self.dt.create_person_or_organisation(primary_name="Test Author")
        addressee_id = self.dt.create_person_or_organisation(primary_name="Test Addressee")
        mentioned_id = self.dt.create_person_or_organisation(primary_name="Mentioned Person")

        # Create locations
        origin_id = self.dt.create_location(element_4_eg_city="London")
        dest_id = self.dt.create_location(element_4_eg_city="Paris")

        # Create work
        work_id = self.dt.create_work(
            work_id_end="test_full",
            description="Test letter",
            date_of_work_std_year=1650,
            date_of_work_std_month=6,
            date_of_work_std_day=15,
            origin_as_marked="London",
            destination_as_marked="Paris"
        )

        # Link author, addressee, mentioned
        self.dt.create_relationship_created(author_id, work_id)
        self.dt.create_relationship_addressed_to(work_id, addressee_id)
        self.dt.create_relationship_mentions(work_id, mentioned_id)

        # Link locations
        self.dt.create_relationship_was_sent_from(work_id, origin_id)
        self.dt.create_relationship_was_sent_to(work_id, dest_id)

        # Add resource
        resource_id = self.dt.create_resource("Work resource", "http://example.com")
        self.dt.create_relationship_work_resource(work_id, resource_id)

        # Add various notes
        date_note_id = self.dt.create_comment("Note on date")
        self.dt.create_relationship_note_on_work_date(date_note_id, work_id)

        addressee_note_id = self.dt.create_comment("Note on addressee")
        self.dt.create_relationship_note_on_work_addressee(addressee_note_id, work_id)

        general_note_id = self.dt.create_comment("General note")
        self.dt.create_relationship_note_on_work_generally(general_note_id, work_id)

        people_note_id = self.dt.create_comment("Note on people mentioned")
        self.dt.create_relationship_note_on_work_people_mentioned(people_note_id, work_id)

        author_note_id = self.dt.create_comment("Note on author")
        self.dt.create_relationship_note_on_work_author(author_note_id, work_id)

        # Verify relationships
        author_maps = self.dt.get_work_person_maps(work_id=work_id, relationship_type=REL_TYPE_CREATED)
        self.assertEqual(len(author_maps), 1)

        location_maps = self.dt.get_work_location_maps(work_id=work_id)
        self.assertEqual(len(location_maps), 2)

        comment_maps = self.dt.get_work_comment_maps(work_id=work_id)
        self.assertEqual(len(comment_maps), 5)

    # === Pattern from tweak_del_morris1-rel.py / tweak_morris1-relations.py ===
    def test_work_to_work_relationships(self):
        """Create work-to-work relationships (reply_to, matches)."""
        work1_id = self.dt.create_work(work_id_end="test_w1", description="Work 1")
        work2_id = self.dt.create_work(work_id_end="test_w2", description="Work 2")

        # Reply relationship
        self.dt.create_relationship_work_reply_to(work2_id, work1_id)

        maps = self.dt.get_work_work_maps(work_from_id=work2_id)
        self.assertGreaterEqual(len(maps), 1)

    # === Pattern from tweak_dewitt-manifestations.py ===
    def test_manifestation_update_printed_edition(self):
        """Update manifestation printed_edition_details."""
        work_id = self.dt.create_work(work_id_end="test_dewitt", description="Test")
        manif_id = self.dt.create_manifestation("test_dewitt_001", work_id=work_id, manifestation_type="P")

        self.dt.update_manifestation(manif_id, {
            "printed_edition_details": "Volume 1, pp. 123-456"
        })

        manif = self.dt.get_manifestation_from_manifestation_id(manif_id)
        self.assertIn("Volume 1", manif['printed_edition_details'])


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestDuplicateRelationshipDetection(TransactionTestCase):
    """Test that creating duplicate relationships raises DuplicateRelationshipError."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def test_duplicate_work_person_map(self):
        from tweaker import DuplicateRelationshipError
        work_id = self.dt.create_work(work_id_end="dup_wp")
        person_id = self.dt.create_person_or_organisation(primary_name="Dup Test Person")

        self.dt.create_relationship_created(person_id, work_id)
        with self.assertRaises(DuplicateRelationshipError):
            self.dt.create_relationship_created(person_id, work_id)

    def test_duplicate_work_location_map(self):
        from tweaker import DuplicateRelationshipError
        work_id = self.dt.create_work(work_id_end="dup_wl")
        location_id = self.dt.create_location(element_4_eg_city="Dup City")

        self.dt.create_relationship_was_sent_from(work_id, location_id)
        with self.assertRaises(DuplicateRelationshipError):
            self.dt.create_relationship_was_sent_from(work_id, location_id)

    def test_duplicate_work_comment_map(self):
        from tweaker import DuplicateRelationshipError
        work_id = self.dt.create_work(work_id_end="dup_wc")
        comment_id = self.dt.create_comment("Dup comment")

        self.dt.create_relationship_note_on_work_generally(comment_id, work_id)
        with self.assertRaises(DuplicateRelationshipError):
            self.dt.create_relationship_note_on_work_generally(comment_id, work_id)

    def test_duplicate_work_resource_map(self):
        from tweaker import DuplicateRelationshipError
        work_id = self.dt.create_work(work_id_end="dup_wr")
        resource_id = self.dt.create_resource("Dup Resource", "http://example.com/dup")

        self.dt.create_work_resource_map(work_id, resource_id)
        with self.assertRaises(DuplicateRelationshipError):
            self.dt.create_work_resource_map(work_id, resource_id)

    def test_duplicate_person_location_map(self):
        from tweaker import DuplicateRelationshipError
        person_id = self.dt.create_person_or_organisation(primary_name="Dup PL Person")
        location_id = self.dt.create_location(element_4_eg_city="Birth City")

        self.dt.create_relationship_person_born_in(person_id, location_id)
        with self.assertRaises(DuplicateRelationshipError):
            self.dt.create_relationship_person_born_in(person_id, location_id)

    def test_same_entities_different_rel_type_allowed(self):
        """Same entities with different relationship type should not raise."""
        work_id = self.dt.create_work(work_id_end="diff_rel")
        person_id = self.dt.create_person_or_organisation(primary_name="Multi Rel Person")

        recref1 = self.dt.create_relationship_created(person_id, work_id)
        recref2 = self.dt.create_relationship_addressed_to(work_id, person_id)

        self.assertIsNotNone(recref1)
        self.assertIsNotNone(recref2)
        self.assertNotEqual(recref1, recref2)

    def test_skip_duplicate_check_bypasses_detection(self):
        """skip_duplicate_check=True should allow creating duplicates."""
        work_id = self.dt.create_work(work_id_end="skip_dup")
        person_id = self.dt.create_person_or_organisation(primary_name="Skip Dup Person")

        self.dt.create_work_person_map(work_id, person_id, REL_TYPE_CREATED)
        # This should not raise because we bypass the check
        recref2 = self.dt._create_map_entry(
            "cofk_work_person_map",
            {"work_id": work_id, "person_id": person_id},
            REL_TYPE_CREATED,
            "work_person_map",
            skip_duplicate_check=True
        )
        self.assertIsNotNone(recref2)


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestRelationshipTypeValidationIntegration(TransactionTestCase):
    """Test that invalid relationship types are rejected on real DB."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def test_invalid_type_raises_error(self):
        from tweaker import InvalidRelationshipTypeError
        work_id = self.dt.create_work(work_id_end="val_test")
        person_id = self.dt.create_person_or_organisation(primary_name="Val Test Person")

        with self.assertRaises(InvalidRelationshipTypeError):
            self.dt.create_work_person_map(work_id, person_id, "totally_invalid_type")

    def test_valid_type_still_works(self):
        work_id = self.dt.create_work(work_id_end="val_ok")
        person_id = self.dt.create_person_or_organisation(primary_name="Val OK Person")

        recref_id = self.dt.create_relationship_created(person_id, work_id)
        self.assertIsNotNone(recref_id)


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestDeleteMapMethods(TransactionTestCase):
    """Test create-then-delete for mapping tables, verify maps are empty after delete."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def _create_work_and_person(self, suffix="del"):
        work_id = self.dt.create_work(work_id_end=f"del_{suffix}")
        person_id = self.dt.create_person_or_organisation(primary_name=f"Del {suffix}")
        return work_id, person_id

    def test_delete_work_person_map(self):
        work_id, person_id = self._create_work_and_person("wp")
        recref_id = self.dt.create_relationship_created(person_id, work_id)
        self.dt.delete_work_person_map(recref_id)
        maps = self.dt.get_work_person_maps(work_id=work_id)
        self.assertEqual(len(maps), 0)

    def test_delete_work_location_map(self):
        work_id = self.dt.create_work(work_id_end="del_wl")
        location_id = self.dt.create_location(element_4_eg_city="Del City")
        recref_id = self.dt.create_relationship_was_sent_from(work_id, location_id)
        self.dt.delete_work_location_map(recref_id)
        maps = self.dt.get_work_location_maps(work_id=work_id)
        self.assertEqual(len(maps), 0)

    def test_delete_work_comment_map(self):
        work_id = self.dt.create_work(work_id_end="del_wc")
        comment_id = self.dt.create_comment("Delete comment test")
        recref_id = self.dt.create_relationship_note_on_work_generally(comment_id, work_id)
        self.dt.delete_work_comment_map(recref_id)
        maps = self.dt.get_work_comment_maps(work_id=work_id)
        self.assertEqual(len(maps), 0)

    def test_delete_work_resource_map(self):
        work_id = self.dt.create_work(work_id_end="del_wr")
        resource_id = self.dt.create_resource("Del Resource", "http://example.com/del")
        recref_id = self.dt.create_work_resource_map(work_id, resource_id)
        self.dt.delete_work_resource_map(recref_id)
        maps = self.dt.get_work_resource_maps(work_id=work_id)
        self.assertEqual(len(maps), 0)

    def test_delete_work_work_map(self):
        work1_id = self.dt.create_work(work_id_end="del_ww1")
        work2_id = self.dt.create_work(work_id_end="del_ww2")
        recref_id = self.dt.create_relationship_work_reply_to(work1_id, work2_id)
        self.dt.delete_work_work_map(recref_id)
        maps = self.dt.get_work_work_maps(work_from_id=work1_id)
        self.assertEqual(len(maps), 0)

    def test_delete_person_comment_map(self):
        person_id = self.dt.create_person_or_organisation(primary_name="Del PC Person")
        comment_id = self.dt.create_comment("Person comment delete test")
        recref_id = self.dt.create_relationship_note_on_person(comment_id, person_id)
        self.dt.delete_person_comment_map(recref_id)
        # Verify via raw query since there's no dedicated get method for person_comment
        maps = self.dt._get_many("cofk_person_comment_map", person_id=person_id)
        self.assertEqual(len(maps), 0)

    def test_delete_person_resource_map(self):
        person_id = self.dt.create_person_or_organisation(primary_name="Del PR Person")
        resource_id = self.dt.create_resource("Person Res Del", "http://example.com/pr_del")
        recref_id = self.dt.create_person_resource_map(person_id, resource_id)
        self.dt.delete_person_resource_map(recref_id)
        maps = self.dt._get_many("cofk_person_resource_map", person_id=person_id)
        self.assertEqual(len(maps), 0)

    def test_delete_person_location_map(self):
        person_id = self.dt.create_person_or_organisation(primary_name="Del PL Person")
        location_id = self.dt.create_location(element_4_eg_city="Del PL City")
        recref_id = self.dt.create_relationship_person_born_in(person_id, location_id)
        self.dt.delete_person_location_map(recref_id)
        maps = self.dt._get_many("cofk_person_location_map", person_id=person_id)
        self.assertEqual(len(maps), 0)

    def test_delete_nonexistent_recref_is_silent(self):
        """Deleting a nonexistent recref_id should not raise."""
        self.dt.delete_work_person_map(999999999)


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestInstitutionMethods(TransactionTestCase):
    """Test institution-related methods."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def test_get_nonexistent_institution_returns_none(self):
        result = self.dt.get_institution_from_institution_id(999999999)
        self.assertIsNone(result)

    def test_update_institution_round_trip(self):
        """Insert an institution via raw SQL, then update and verify."""
        inst_id = self.dt.execute_scalar(
            "INSERT INTO cofk_union_institution (institution_name, creation_user, change_user) "
            "VALUES (:name, :user, :user) RETURNING institution_id",
            {"name": "Test Institution", "user": self.dt.user}
        )
        self.assertIsNotNone(inst_id)

        self.dt.update_institution(inst_id, {"institution_name": "Updated Institution"})

        inst = self.dt.get_institution_from_institution_id(inst_id)
        self.assertEqual(inst['institution_name'], "Updated Institution")


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestLanguageMethods(TransactionTestCase):
    """Test language-related methods."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def test_add_language_to_work_is_idempotent(self):
        """add_language_to_work uses ON CONFLICT DO NOTHING, so calling twice should not raise."""
        work_id = self.dt.create_work(work_id_end="lang_w")
        self.dt.add_language_to_work(work_id, "eng")
        # Second call should be a no-op (not raise)
        self.dt.add_language_to_work(work_id, "eng")

    def test_add_language_to_manifestation_is_idempotent(self):
        """add_language_to_manifestation uses ON CONFLICT DO NOTHING."""
        work_id = self.dt.create_work(work_id_end="lang_m")
        manif_id = self.dt.create_manifestation("lang_manif_001", work_id=work_id, manifestation_type="ALS")
        self.dt.add_language_to_manifestation(manif_id, "eng")
        # Second call should be a no-op (not raise)
        self.dt.add_language_to_manifestation(manif_id, "eng")

    def test_get_languages_from_code(self):
        """get_languages_from_code should return language names from ISO codes."""
        result = self.dt.get_languages_from_code("eng")
        self.assertIsInstance(result, str)
        # If the iso_639_language_codes table is populated, should contain "English"
        # If not populated, result will be empty string
        # Either way, it should not raise


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestErrorPaths(TransactionTestCase):
    """Test various error and edge-case paths."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def test_nonexistent_ids_return_none(self):
        """All get-by-id methods should return None for nonexistent IDs."""
        self.assertIsNone(self.dt.get_work_from_iwork_id(999999999))
        self.assertIsNone(self.dt.get_work_from_work_id("nonexistent_work_id"))
        self.assertIsNone(self.dt.get_person_from_person_id("nonexistent_person"))
        self.assertIsNone(self.dt.get_person_from_iperson_id(999999999))
        self.assertIsNone(self.dt.get_location_from_location_id(999999999))
        self.assertIsNone(self.dt.get_comment_from_comment_id(999999999))
        self.assertIsNone(self.dt.get_resource_from_resource_id(999999999))
        self.assertIsNone(self.dt.get_image_from_image_id(999999999))
        self.assertIsNone(self.dt.get_institution_from_institution_id(999999999))
        self.assertIsNone(self.dt.get_manifestation_from_manifestation_id("nonexistent_manif"))

    def test_bad_sql_raises_in_execute_raw(self):
        """execute_raw should propagate errors on invalid SQL."""
        with self.assertRaises(Exception):
            self.dt.execute_raw("SELECT * FROM nonexistent_table_xyz_999")

    def test_bad_sql_raises_in_execute_scalar(self):
        """execute_scalar should propagate errors on invalid SQL."""
        from sqlalchemy.exc import SQLAlchemyError
        with self.assertRaises(SQLAlchemyError) as ctx:
            self.dt.execute_scalar("SELECT * FROM nonexistent_table_xyz_999")
        self.assertIn("nonexistent_table_xyz_999", str(ctx.exception))

    def test_update_with_empty_dict_is_noop(self):
        """update_* with empty field_updates should be a no-op (not crash)."""
        work_id = self.dt.create_work(work_id_end="noop_upd")
        self.dt.update_work(work_id, {})
        # Should still be retrievable and unchanged
        work = self.dt.get_work_from_work_id(work_id)
        self.assertIsNotNone(work)

    def test_query_maps_on_work_with_no_relationships_returns_empty(self):
        """Querying mapping tables on a work with no relationships should return []."""
        work_id = self.dt.create_work(work_id_end="no_rels")
        self.assertEqual(self.dt.get_work_person_maps(work_id=work_id), [])
        self.assertEqual(self.dt.get_work_location_maps(work_id=work_id), [])
        self.assertEqual(self.dt.get_work_comment_maps(work_id=work_id), [])
        self.assertEqual(self.dt.get_work_resource_maps(work_id=work_id), [])
        self.assertEqual(self.dt.get_work_work_maps(work_from_id=work_id), [])


if __name__ == '__main__':
    unittest.main()
