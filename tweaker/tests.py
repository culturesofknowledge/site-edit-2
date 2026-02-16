# -*- coding: utf-8 -*-
"""
Unit and integration tests for the Tweaker module.

Run unit tests standalone (no Django required):
    python -m tweaker.tests

Run all tests with Django:
    python manage.py test tweaker

Run specific test classes:
    python manage.py test tweaker.tests.TestUtilityMethods
    python manage.py test tweaker.tests.TestDatabaseTweakerIntegration
"""
import unittest
from unittest.mock import MagicMock, patch

# Try to import Django test classes - they're optional for unit tests
try:
    from django.test import TestCase, TransactionTestCase
    from django.conf import settings
    DJANGO_AVAILABLE = True
except ImportError:
    # Create dummy classes if Django isn't available
    TransactionTestCase = unittest.TestCase
    DJANGO_AVAILABLE = False

# Try to import core constants - they're optional for unit tests
try:
    from core.constant import (
        REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM,
        REL_TYPE_WAS_SENT_TO, REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_IS_RELATED_TO,
    )
    CORE_AVAILABLE = True
except ImportError:
    # Define constants locally if core module isn't available
    REL_TYPE_CREATED = 'created'
    REL_TYPE_WAS_ADDRESSED_TO = 'was_addressed_to'
    REL_TYPE_WAS_SENT_FROM = 'was_sent_from'
    REL_TYPE_WAS_SENT_TO = 'was_sent_to'
    REL_TYPE_COMMENT_REFERS_TO = 'refers_to'
    REL_TYPE_IS_RELATED_TO = 'is_related_to'
    CORE_AVAILABLE = False


class TestUtilityMethods(unittest.TestCase):
    """Test utility/static methods that don't require database."""

    def test_get_int_value_with_int(self):
        from tweaker import DatabaseTweaker
        self.assertEqual(DatabaseTweaker.get_int_value(42), 42)

    def test_get_int_value_with_string(self):
        from tweaker import DatabaseTweaker
        self.assertEqual(DatabaseTweaker.get_int_value("123"), 123)

    def test_get_int_value_with_none(self):
        from tweaker import DatabaseTweaker
        self.assertIsNone(DatabaseTweaker.get_int_value(None))

    def test_get_int_value_with_empty_string(self):
        from tweaker import DatabaseTweaker
        self.assertIsNone(DatabaseTweaker.get_int_value(""))

    def test_get_int_value_with_default(self):
        from tweaker import DatabaseTweaker
        self.assertEqual(DatabaseTweaker.get_int_value(None, 0), 0)
        self.assertEqual(DatabaseTweaker.get_int_value("", 99), 99)

    def test_get_date_string_full_date(self):
        from tweaker import DatabaseTweaker
        result = DatabaseTweaker.get_date_string(2023, 5, 15)
        self.assertEqual(result, "2023-05-15")

    def test_get_date_string_year_only(self):
        from tweaker import DatabaseTweaker
        result = DatabaseTweaker.get_date_string(2023, None, None)
        self.assertEqual(result, "2023-12-31")

    def test_get_date_string_year_month(self):
        from tweaker import DatabaseTweaker
        # February should default to 28
        result = DatabaseTweaker.get_date_string(2023, 2, None)
        self.assertEqual(result, "2023-02-28")

        # April should default to 30
        result = DatabaseTweaker.get_date_string(2023, 4, None)
        self.assertEqual(result, "2023-04-30")

        # January should default to 31
        result = DatabaseTweaker.get_date_string(2023, 1, None)
        self.assertEqual(result, "2023-01-31")

    def test_get_date_string_none_values(self):
        from tweaker import DatabaseTweaker
        result = DatabaseTweaker.get_date_string(None, None, None)
        self.assertEqual(result, "9999-12-31")

    def test_get_date_string_formatting(self):
        from tweaker import DatabaseTweaker
        # Test that single digit values are zero-padded
        result = DatabaseTweaker.get_date_string(800, 1, 5)
        self.assertEqual(result, "0800-01-05")

    def test_get_csv_data(self):
        from tweaker import DatabaseTweaker
        import tempfile
        import os

        # Create a temporary CSV file
        csv_content = "name,age,city\nAlice,30,London\nBob,25,Paris\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            rows = DatabaseTweaker.get_csv_data(temp_path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['name'], 'Alice')
            self.assertEqual(rows[0]['age'], '30')
            self.assertEqual(rows[1]['city'], 'Paris')
        finally:
            os.unlink(temp_path)


class TestCalendarConversion(unittest.TestCase):
    """Test Julian to Gregorian calendar conversion."""

    def test_julian_to_gregorian_1600s(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        # In 1600s, the difference is 10 days
        result = dt.calendar_julian_to_calendar_gregorian(15, 6, 1650)
        self.assertEqual(result['d'], 25)
        self.assertEqual(result['m'], 6)
        self.assertEqual(result['y'], 1650)

    def test_julian_to_gregorian_1700s(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        # After 1700, the difference is 11 days
        result = dt.calendar_julian_to_calendar_gregorian(15, 6, 1750)
        self.assertEqual(result['d'], 26)
        self.assertEqual(result['m'], 6)
        self.assertEqual(result['y'], 1750)

    def test_julian_to_gregorian_month_overflow(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        # Dec 25 + 10 days = Jan 4 next year
        result = dt.calendar_julian_to_calendar_gregorian(25, 12, 1650)
        self.assertEqual(result['d'], 4)
        self.assertEqual(result['m'], 1)
        self.assertEqual(result['y'], 1651)


class TestDatabaseTweakerInit(unittest.TestCase):
    """Test DatabaseTweaker initialization without actual database."""

    def test_init_without_connection(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        self.assertIsNone(dt.engine)
        self.assertIsNone(dt.connection)
        self.assertEqual(dt.user, "cofkbot")
        self.assertFalse(dt.debug)

    def test_init_with_debug(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker(debug=True)
        self.assertTrue(dt.debug)

    def test_database_ok_when_not_connected(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()
        self.assertFalse(dt.database_ok())

    def test_audit_tracking(self):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()

        # Test audit methods
        dt._audit_insert("work")
        dt._audit_insert("work")
        dt._audit_insert("person")
        self.assertEqual(dt.audit["insertions"]["work"], 2)
        self.assertEqual(dt.audit["insertions"]["person"], 1)

        dt._audit_update("work")
        self.assertEqual(dt.audit["updates"]["work"], 1)

        dt._audit_delete("comment")
        self.assertEqual(dt.audit["deletions"]["comment"], 1)

        # Test reset
        dt._reset_audit()
        self.assertEqual(dt.audit["insertions"], {})
        self.assertEqual(dt.audit["updates"], {})
        self.assertEqual(dt.audit["deletions"], {})


class TestDatabaseTweakerMocked(unittest.TestCase):
    """Test DatabaseTweaker methods with mocked database."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker()
        # Mock the database connection
        self.dt.engine = MagicMock()
        self.dt.connection = MagicMock()
        self.dt.metadata = MagicMock()

    def test_check_database_connection_when_connected(self):
        # Should not raise when connected
        self.dt.check_database_connection()

    def test_check_database_connection_when_not_connected(self):
        from sqlalchemy.exc import SQLAlchemyError
        self.dt.engine = None
        self.dt.connection = None
        with self.assertRaises(SQLAlchemyError):
            self.dt.check_database_connection()

    def test_close(self):
        self.dt.close()
        self.assertIsNone(self.dt.engine)
        self.assertIsNone(self.dt.connection)
        self.assertIsNone(self.dt.metadata)
        self.assertEqual(self.dt._tables, {})


@unittest.skipUnless(DJANGO_AVAILABLE, "Django not available")
class TestDatabaseTweakerIntegration(TransactionTestCase):
    """
    Integration tests that use the actual Django test database via SQLAlchemy.

    These tests require the database schema to be set up (migrations applied).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get database settings from Django
        cls.db_settings = settings.DATABASES['default']

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker.from_django_settings()

    def tearDown(self):
        # Rollback any changes
        if self.dt.connection:
            self.dt.commit_changes(commit=False, quiet=True)
            self.dt.close()

    def test_connection_from_django_settings(self):
        """Test that we can connect using Django settings."""
        self.assertTrue(self.dt.database_ok())

    def test_create_and_get_location(self):
        """Test creating and retrieving a location."""
        location_id = self.dt.create_location(
            element_4_eg_city="Test City",
            element_6_eg_country="Test Country",
            editors_notes="Test note"
        )

        self.assertIsNotNone(location_id)
        self.assertIsInstance(location_id, int)

        # Retrieve the location
        location = self.dt.get_location_from_location_id(location_id)
        self.assertIsNotNone(location)
        self.assertEqual(location['element_4_eg_city'], "Test City")
        self.assertEqual(location['element_6_eg_country'], "Test Country")
        self.assertIn("Test City", location['location_name'])

        # Check audit
        self.assertEqual(self.dt.audit["insertions"]["location"], 1)

    def test_create_and_get_comment(self):
        """Test creating and retrieving a comment."""
        comment_text = "This is a test comment"
        comment_id = self.dt.create_comment(comment_text)

        self.assertIsNotNone(comment_id)
        self.assertIsInstance(comment_id, int)

        # Retrieve the comment
        comment = self.dt.get_comment_from_comment_id(comment_id)
        self.assertIsNotNone(comment)
        self.assertEqual(comment['comment'], comment_text)

    def test_create_and_get_resource(self):
        """Test creating and retrieving a resource."""
        resource_id = self.dt.create_resource(
            name="Test Resource",
            url="https://example.com/test",
            description="A test resource"
        )

        self.assertIsNotNone(resource_id)

        # Retrieve the resource
        resource = self.dt.get_resource_from_resource_id(resource_id)
        self.assertIsNotNone(resource)
        self.assertEqual(resource['resource_name'], "Test Resource")
        self.assertEqual(resource['resource_url'], "https://example.com/test")

    def test_create_person(self):
        """Test creating a person."""
        person_id = self.dt.create_person_or_organisation(
            primary_name="John Test",
            gender='M',
            birth_year=1800,
            death_year=1870,
            editors_notes="Test person"
        )

        self.assertIsNotNone(person_id)
        self.assertIn("cofk_union_person", person_id)

        # Retrieve the person
        person = self.dt.get_person_from_person_id(person_id)
        self.assertIsNotNone(person)
        self.assertEqual(person['foaf_name'], "John Test")
        self.assertEqual(person['gender'], 'M')
        self.assertEqual(person['date_of_birth_year'], 1800)
        self.assertEqual(person['date_of_death_year'], 1870)

    def test_create_organisation(self):
        """Test creating an organisation."""
        org_id = self.dt.create_person_or_organisation(
            primary_name="Test University",
            is_org='Y',
            editors_notes="Test organisation"
        )

        self.assertIsNotNone(org_id)

        org = self.dt.get_person_from_person_id(org_id)
        self.assertEqual(org['is_organisation'], 'Y')
        self.assertEqual(org['foaf_name'], "Test University")

    def test_create_work(self):
        """Test creating a work."""
        work_id = self.dt.create_work(
            work_id_end="test_suffix",
            description="A test letter",
            date_of_work_std_year=1650,
            date_of_work_std_month=6,
            date_of_work_std_day=15,
            origin_as_marked="London",
            destination_as_marked="Paris"
        )

        self.assertIsNotNone(work_id)
        self.assertIn("work_", work_id)
        self.assertIn("test_suffix", work_id)

        # Retrieve the work
        work = self.dt.get_work_from_work_id(work_id)
        self.assertIsNotNone(work)
        self.assertEqual(work['description'], "A test letter")
        self.assertEqual(work['date_of_work_std_year'], 1650)

    def test_update_location(self):
        """Test updating a location."""
        location_id = self.dt.create_location(
            element_4_eg_city="Original City"
        )

        self.dt.update_location(location_id, {"element_4_eg_city": "Updated City"})

        location = self.dt.get_location_from_location_id(location_id)
        self.assertEqual(location['element_4_eg_city'], "Updated City")
        self.assertEqual(self.dt.audit["updates"]["location"], 1)

    def test_update_comment(self):
        """Test updating a comment."""
        comment_id = self.dt.create_comment("Original comment")

        self.dt.update_comment(comment_id, {"comment": "Updated comment"})

        comment = self.dt.get_comment_from_comment_id(comment_id)
        self.assertEqual(comment['comment'], "Updated comment")

    def test_create_work_location_relationship(self):
        """Test creating work-location relationships."""
        # Create work and location
        work_id = self.dt.create_work(work_id_end="rel_test")
        location_id = self.dt.create_location(element_4_eg_city="Test Origin")

        # Create origin relationship
        recref_id = self.dt.create_relationship_was_sent_from(work_id, location_id)
        self.assertIsNotNone(recref_id)

        # Query the relationship
        maps = self.dt.get_work_location_maps(
            work_id=work_id,
            relationship_type=REL_TYPE_WAS_SENT_FROM
        )
        self.assertEqual(len(maps), 1)
        self.assertEqual(maps[0]['location_id'], location_id)

    def test_create_work_person_relationship(self):
        """Test creating work-person relationships."""
        work_id = self.dt.create_work(work_id_end="person_rel_test")
        person_id = self.dt.create_person_or_organisation(primary_name="Test Author")

        # Create author relationship
        recref_id = self.dt.create_relationship_created(person_id, work_id)
        self.assertIsNotNone(recref_id)

        # Query the relationship
        maps = self.dt.get_work_person_maps(
            work_id=work_id,
            relationship_type=REL_TYPE_CREATED
        )
        self.assertEqual(len(maps), 1)
        self.assertEqual(maps[0]['person_id'], person_id)

    def test_execute_raw_sql(self):
        """Test executing raw SQL queries."""
        result = self.dt.execute_raw("SELECT 1 as value")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 1)

    def test_execute_scalar(self):
        """Test executing scalar SQL queries."""
        result = self.dt.execute_scalar("SELECT 42")
        self.assertEqual(result, 42)

    def test_commit_rollback(self):
        """Test commit and rollback functionality."""
        # Create something
        location_id = self.dt.create_location(element_4_eg_city="Rollback Test")

        # Rollback
        self.dt.commit_changes(commit=False, quiet=True)

        # After rollback, the location should not be findable in a new connection
        # (but in this same transaction it might still be visible)
        # This mainly tests that the method doesn't crash

    def test_get_nonexistent_record_returns_none(self):
        """Test that getting a non-existent record returns None."""
        work = self.dt.get_work_from_iwork_id(999999999)
        self.assertIsNone(work)

        person = self.dt.get_person_from_person_id("nonexistent_person_id")
        self.assertIsNone(person)

        location = self.dt.get_location_from_location_id(999999999)
        self.assertIsNone(location)


class TestLegacyConnectionString(unittest.TestCase):
    """Test backwards compatibility with old psycopg2 connection string format."""

    @patch.object(__import__('tweaker').DatabaseTweaker, 'connect')
    def test_connect_to_postgres_parses_old_format(self, mock_connect):
        from tweaker import DatabaseTweaker
        dt = DatabaseTweaker()

        old_format = "dbname='testdb' host='localhost' port='5432' user='testuser' password='testpass'"
        dt.connect_to_postgres(old_format)

        # Check that connect was called with a properly formatted SQLAlchemy URL
        mock_connect.assert_called_once()
        url = mock_connect.call_args[0][0]
        self.assertIn("postgresql://", url)
        self.assertIn("testuser", url)
        self.assertIn("testpass", url)
        self.assertIn("localhost", url)
        self.assertIn("5432", url)
        self.assertIn("testdb", url)


class TestRelationshipTypeValidation(unittest.TestCase):
    """Verify the VALID_RELATIONSHIP_TYPES dict exists, covers all mapping tables,
    and contains only non-empty strings."""

    def test_valid_relationship_types_exists(self):
        from tweaker.tweaker import VALID_RELATIONSHIP_TYPES
        self.assertIsInstance(VALID_RELATIONSHIP_TYPES, dict)
        self.assertGreater(len(VALID_RELATIONSHIP_TYPES), 0)

    def test_covers_all_expected_mapping_tables(self):
        from tweaker.tweaker import VALID_RELATIONSHIP_TYPES
        expected_tables = {
            "cofk_work_person_map",
            "cofk_work_location_map",
            "cofk_work_comment_map",
            "cofk_work_resource_map",
            "cofk_work_work_map",
            "cofk_person_comment_map",
            "cofk_person_resource_map",
            "cofk_person_location_map",
            "cofk_manif_comment_map",
            "cofk_manif_inst_map",
        }
        self.assertEqual(set(VALID_RELATIONSHIP_TYPES.keys()), expected_tables)

    def test_values_are_non_empty_string_sets(self):
        from tweaker.tweaker import VALID_RELATIONSHIP_TYPES
        for table_name, valid_types in VALID_RELATIONSHIP_TYPES.items():
            self.assertIsInstance(valid_types, set, f"{table_name} should map to a set")
            self.assertGreater(len(valid_types), 0, f"{table_name} should have at least one valid type")
            for rel_type in valid_types:
                self.assertIsInstance(rel_type, str, f"Types in {table_name} should be strings")
                self.assertGreater(len(rel_type), 0, f"Types in {table_name} should be non-empty")


class TestCustomExceptions(unittest.TestCase):
    """Verify the custom exception class hierarchy."""

    def test_tweaker_error_inherits_from_exception(self):
        from tweaker import TweakerError
        self.assertTrue(issubclass(TweakerError, Exception))

    def test_duplicate_relationship_error_inherits_from_tweaker_error(self):
        from tweaker import DuplicateRelationshipError, TweakerError
        self.assertTrue(issubclass(DuplicateRelationshipError, TweakerError))
        self.assertTrue(issubclass(DuplicateRelationshipError, Exception))

    def test_invalid_relationship_type_error_inherits_from_tweaker_error(self):
        from tweaker import InvalidRelationshipTypeError, TweakerError
        self.assertTrue(issubclass(InvalidRelationshipTypeError, TweakerError))
        self.assertTrue(issubclass(InvalidRelationshipTypeError, Exception))

    def test_exceptions_can_be_raised_and_caught(self):
        from tweaker import TweakerError, DuplicateRelationshipError, InvalidRelationshipTypeError

        with self.assertRaises(TweakerError):
            raise DuplicateRelationshipError("test duplicate")

        with self.assertRaises(TweakerError):
            raise InvalidRelationshipTypeError("test invalid type")


class TestCreateMapEntryValidationMocked(unittest.TestCase):
    """Test that invalid relationship types raise InvalidRelationshipTypeError
    using mocked database (no actual DB needed)."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker()
        self.dt.engine = MagicMock()
        self.dt.connection = MagicMock()
        self.dt.metadata = MagicMock()

    def test_invalid_type_for_work_person_map(self):
        from tweaker import InvalidRelationshipTypeError
        with self.assertRaises(InvalidRelationshipTypeError):
            self.dt.create_work_person_map("work_123", "person_456", "bogus_type")

    def test_invalid_type_for_work_location_map(self):
        from tweaker import InvalidRelationshipTypeError
        with self.assertRaises(InvalidRelationshipTypeError):
            self.dt.create_work_location_map("work_123", 1, "not_a_valid_type")

    def test_invalid_type_for_work_work_map(self):
        from tweaker import InvalidRelationshipTypeError
        with self.assertRaises(InvalidRelationshipTypeError):
            self.dt.create_work_work_map("work_1", "work_2", "invalid_relation")

    def test_invalid_type_for_person_location_map(self):
        from tweaker import InvalidRelationshipTypeError
        with self.assertRaises(InvalidRelationshipTypeError):
            self.dt.create_person_location_map("person_1", 1, "wrong_type")

    def test_error_message_includes_table_and_type(self):
        from tweaker import InvalidRelationshipTypeError
        with self.assertRaises(InvalidRelationshipTypeError) as ctx:
            self.dt.create_work_person_map("work_123", "person_456", "bogus")
        self.assertIn("cofk_work_person_map", str(ctx.exception))
        self.assertIn("bogus", str(ctx.exception))


class TestExecuteRawErrorHandling(unittest.TestCase):
    """Test execute_raw and execute_scalar error handling with mocked connection."""

    def setUp(self):
        from tweaker import DatabaseTweaker
        self.dt = DatabaseTweaker()
        self.dt.engine = MagicMock()
        self.dt.connection = MagicMock()
        self.dt.metadata = MagicMock()

    def test_execute_raw_returns_empty_for_non_select(self):
        """Non-SELECT statements (INSERT/UPDATE/DELETE) raise ResourceClosedError
        when iterating results — execute_raw should return []."""
        from sqlalchemy.exc import ResourceClosedError
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(side_effect=ResourceClosedError("This result object does not return rows."))
        self.dt.connection.execute.return_value = mock_result

        result = self.dt.execute_raw("INSERT INTO foo VALUES (1)")
        self.assertEqual(result, [])

    def test_execute_raw_propagates_real_db_errors(self):
        """Real database errors (e.g., ProgrammingError) should propagate."""
        from sqlalchemy.exc import ProgrammingError
        self.dt.connection.execute.side_effect = ProgrammingError(
            "statement", {}, Exception("relation does not exist")
        )

        with self.assertRaises(ProgrammingError):
            self.dt.execute_raw("SELECT * FROM nonexistent_table")

    def test_execute_scalar_adds_sql_context_to_errors(self):
        """execute_scalar should wrap SQLAlchemyError with the SQL statement in the message."""
        from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
        self.dt.connection.execute.side_effect = ProgrammingError(
            "statement", {}, Exception("column does not exist")
        )

        with self.assertRaises(SQLAlchemyError) as ctx:
            self.dt.execute_scalar("SELECT bad_column FROM foo")
        self.assertIn("SELECT bad_column FROM foo", str(ctx.exception))

    def test_execute_scalar_returns_none_for_empty_result(self):
        """execute_scalar should return None when no rows are returned."""
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        self.dt.connection.execute.return_value = mock_result

        result = self.dt.execute_scalar("SELECT 1 WHERE false")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
