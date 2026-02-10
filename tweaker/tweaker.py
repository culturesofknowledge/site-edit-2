# -*- coding: utf-8 -*-
"""
Database tweaker for EMLO/CofK database operations.
Synced with site-edit-2 Django models.
Uses SQLAlchemy Core for database operations.
"""
import csv
from datetime import datetime
from typing import Optional, Dict, List, Any

from sqlalchemy import (
    create_engine, MetaData, Table, select, insert, update, delete, text
)
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError, ResourceClosedError

# Import relationship type constants from core
from core.constant import (
    REL_TYPE_COMMENT_REFERS_TO,
    REL_TYPE_COMMENT_AUTHOR,
    REL_TYPE_COMMENT_ADDRESSEE,
    REL_TYPE_COMMENT_DATE,
    REL_TYPE_COMMENT_ORIGIN,
    REL_TYPE_COMMENT_DESTINATION,
    REL_TYPE_COMMENT_ROUTE,
    REL_TYPE_COMMENT_PERSON_MENTIONED,
    REL_TYPE_MENTION_PLACE,
    REL_TYPE_MENTION,
    REL_TYPE_WORK_IS_REPLY_TO,
    REL_TYPE_WORK_MATCHES,
    REL_TYPE_WAS_SENT_TO,
    REL_TYPE_WAS_SENT_FROM,
    REL_TYPE_STORED_IN,
    REL_TYPE_IS_RELATED_TO,
    REL_TYPE_CREATED,
    REL_TYPE_SENT,
    REL_TYPE_SIGNED,
    REL_TYPE_WAS_ADDRESSED_TO,
    REL_TYPE_INTENDED_FOR,
    REL_TYPE_WAS_BORN_IN_LOCATION,
    REL_TYPE_WAS_IN_LOCATION,
    REL_TYPE_DIED_AT_LOCATION,
)


class TweakerError(Exception):
    """Base exception for DatabaseTweaker operations."""


class DuplicateRelationshipError(TweakerError):
    """Raised when creating a relationship that already exists."""


class InvalidRelationshipTypeError(TweakerError):
    """Raised when relationship_type is not valid for the target mapping table."""


# Valid relationship types for each mapping table, derived from the convenience methods.
# Tables not listed here skip validation (forward-compatible).
VALID_RELATIONSHIP_TYPES = {
    "cofk_work_person_map": {
        REL_TYPE_CREATED,
        REL_TYPE_WAS_ADDRESSED_TO,
        REL_TYPE_MENTION,
        REL_TYPE_SIGNED,
        REL_TYPE_SENT,
        REL_TYPE_INTENDED_FOR,
    },
    "cofk_work_location_map": {
        REL_TYPE_WAS_SENT_TO,
        REL_TYPE_WAS_SENT_FROM,
        REL_TYPE_MENTION_PLACE,
    },
    "cofk_work_comment_map": {
        REL_TYPE_COMMENT_REFERS_TO,
        REL_TYPE_COMMENT_AUTHOR,
        REL_TYPE_COMMENT_ADDRESSEE,
        REL_TYPE_COMMENT_DATE,
        REL_TYPE_COMMENT_ORIGIN,
        REL_TYPE_COMMENT_DESTINATION,
        REL_TYPE_COMMENT_ROUTE,
        REL_TYPE_COMMENT_PERSON_MENTIONED,
    },
    "cofk_work_resource_map": {
        REL_TYPE_IS_RELATED_TO,
    },
    "cofk_work_work_map": {
        REL_TYPE_WORK_IS_REPLY_TO,
        REL_TYPE_WORK_MATCHES,
    },
    "cofk_person_comment_map": {
        REL_TYPE_COMMENT_REFERS_TO,
    },
    "cofk_person_resource_map": {
        REL_TYPE_IS_RELATED_TO,
    },
    "cofk_person_location_map": {
        REL_TYPE_WAS_BORN_IN_LOCATION,
        REL_TYPE_WAS_IN_LOCATION,
        REL_TYPE_DIED_AT_LOCATION,
    },
    "cofk_manif_comment_map": {
        REL_TYPE_COMMENT_REFERS_TO,
    },
    "cofk_manif_inst_map": {
        REL_TYPE_STORED_IN,
    },
}


class DatabaseTweaker:
    """
    Database tweaker for CofK/EMLO PostgreSQL database operations.
    Uses SQLAlchemy Core for database operations.

    Uses mapping tables instead of generic relationship table:
    - cofk_work_comment_map, cofk_work_resource_map, cofk_work_person_map,
      cofk_work_location_map, cofk_work_work_map, cofk_work_subject_map
    - cofk_person_location_map, cofk_person_person_map, cofk_person_comment_map,
      cofk_person_resource_map, cofk_person_image_map, cofk_person_role_map
    - cofk_manif_comment_map, cofk_manif_person_map, cofk_manif_manif_map,
      cofk_manif_inst_map, cofk_manif_image_map
    - cofk_location_comment_map, cofk_location_resource_map, cofk_location_image_map
    - cofk_institution_resource_map, cofk_institution_image_map
    """

    @classmethod
    def from_django_settings(cls, debug: bool = False):
        """Create a tweaker using Django database settings."""
        from django.conf import settings
        db = settings.DATABASES['default']

        return cls.tweaker_from_connection(
            dbname=db['NAME'],
            host=db['HOST'],
            port=str(db.get('PORT', 5432)),
            user=db['USER'],
            password=db['PASSWORD'],
            debug=debug
        )

    @classmethod
    def tweaker_from_connection(cls, dbname: str, host: str, port: str,
                                 user: str, password: str, debug: bool = False):
        """Create a tweaker with explicit connection parameters."""
        url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return cls(url, debug)

    def __init__(self, connection_url: Optional[str] = None, debug: bool = False):
        self.debug = False
        self.set_debug(debug)

        self.engine: Optional[Engine] = None
        self.connection: Optional[Connection] = None
        self.metadata: Optional[MetaData] = None
        self._tables: Dict[str, Table] = {}

        if connection_url:
            self.connect(connection_url)

        self._reset_audit()
        self.user = "cofkbot"

    def _reset_audit(self):
        self.audit = {
            "deletions": {},
            "insertions": {},
            "updates": {}
        }

    def set_debug(self, debug: bool):
        self.debug = debug
        if debug:
            print("Debug ON - printing SQL")

    def connect(self, connection_url: str):
        """Connect to the database using SQLAlchemy."""
        try:
            self.engine = create_engine(
                connection_url,
                echo=self.debug,
                pool_pre_ping=True
            )
            self.connection = self.engine.connect()
            self.metadata = MetaData()
            self._tables = {}
            if self.debug:
                print("Connected to database...")
        except SQLAlchemyError as e:
            print(f"ERROR: Unable to connect to the database: {e}")
            raise

    # Backwards compatibility alias
    def connect_to_postgres(self, connection: str):
        """Legacy method - converts psycopg2 connection string to SQLAlchemy URL."""
        # Parse the old format: "dbname='x' host='y' port='z' user='u' password='p'"
        parts = {}
        for part in connection.split("' "):
            if '=' in part:
                key, value = part.split('=', 1)
                parts[key.strip()] = value.strip().strip("'")

        url = (f"postgresql://{parts.get('user', '')}:{parts.get('password', '')}"
               f"@{parts.get('host', 'localhost')}:{parts.get('port', '5432')}"
               f"/{parts.get('dbname', '')}")
        self.connect(url)

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.connection = None
        self.engine = None
        self.metadata = None
        self._tables = {}

    def _get_table(self, table_name: str) -> Table:
        """Get or reflect a table from the database."""
        if table_name not in self._tables:
            self._tables[table_name] = Table(
                table_name, self.metadata,
                autoload_with=self.engine
            )
        return self._tables[table_name]

    # ==================== CSV Utilities ====================

    @staticmethod
    def get_csv_data(filename: str) -> List[Dict]:
        rows = []
        with open(filename, encoding='utf-8') as file:
            csv_file = csv.DictReader(file, dialect=csv.excel)
            for row in csv_file:
                rows.append(row)
        return rows

    # ==================== GET Methods ====================

    def _get_one(self, table_name: str, **conditions) -> Optional[Dict]:
        """Generic method to get a single row from a table."""
        self.check_database_connection()
        table = self._get_table(table_name)

        stmt = select(table)
        for col, val in conditions.items():
            stmt = stmt.where(table.c[col] == val)

        self._print_command(f"SELECT {table_name}", stmt)
        result = self.connection.execute(stmt)
        row = result.fetchone()
        return dict(row._mapping) if row else None

    def _get_many(self, table_name: str, **conditions) -> List[Dict]:
        """Generic method to get multiple rows from a table."""
        self.check_database_connection()
        table = self._get_table(table_name)

        stmt = select(table)
        for col, val in conditions.items():
            if val is not None:
                stmt = stmt.where(table.c[col] == val)

        self._print_command(f"SELECT {table_name}", stmt)
        result = self.connection.execute(stmt)
        return [dict(row._mapping) for row in result]

    def get_work_from_iwork_id(self, iwork_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_work", iwork_id=int(iwork_id))

    def get_work_from_work_id(self, work_id: str) -> Optional[Dict]:
        return self._get_one("cofk_union_work", work_id=work_id)

    def get_resource_from_resource_id(self, resource_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_resource", resource_id=resource_id)

    def get_image_from_image_id(self, image_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_image", image_id=image_id)

    def get_comment_from_comment_id(self, comment_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_comment", comment_id=comment_id)

    def get_institution_from_institution_id(self, institution_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_institution", institution_id=institution_id)

    def get_location_from_location_id(self, location_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_location", location_id=location_id)

    def get_person_from_iperson_id(self, iperson_id: int) -> Optional[Dict]:
        return self._get_one("cofk_union_person", iperson_id=iperson_id)

    def get_person_from_person_id(self, person_id: str) -> Optional[Dict]:
        return self._get_one("cofk_union_person", person_id=person_id)

    def get_manifestation_from_manifestation_id(self, manifestation_id: str) -> Optional[Dict]:
        return self._get_one("cofk_union_manifestation", manifestation_id=manifestation_id)

    # ==================== Mapping Table Queries ====================

    def get_work_person_maps(self, work_id: str = None, person_id: str = None,
                             relationship_type: str = None) -> List[Dict]:
        """Get work-person relationships from cofk_work_person_map."""
        return self._get_many(
            "cofk_work_person_map",
            work_id=work_id,
            person_id=person_id,
            relationship_type=relationship_type
        )

    def get_work_location_maps(self, work_id: str = None, location_id: int = None,
                               relationship_type: str = None) -> List[Dict]:
        """Get work-location relationships from cofk_work_location_map."""
        return self._get_many(
            "cofk_work_location_map",
            work_id=work_id,
            location_id=location_id,
            relationship_type=relationship_type
        )

    def get_work_comment_maps(self, work_id: str = None, comment_id: int = None,
                              relationship_type: str = None) -> List[Dict]:
        """Get work-comment relationships from cofk_work_comment_map."""
        return self._get_many(
            "cofk_work_comment_map",
            work_id=work_id,
            comment_id=comment_id,
            relationship_type=relationship_type
        )

    def get_work_resource_maps(self, work_id: str = None, resource_id: int = None) -> List[Dict]:
        """Get work-resource relationships from cofk_work_resource_map."""
        return self._get_many(
            "cofk_work_resource_map",
            work_id=work_id,
            resource_id=resource_id
        )

    def get_work_work_maps(self, work_from_id: str = None, work_to_id: str = None,
                           relationship_type: str = None) -> List[Dict]:
        """Get work-work relationships from cofk_work_work_map."""
        return self._get_many(
            "cofk_work_work_map",
            work_from_id=work_from_id,
            work_to_id=work_to_id,
            relationship_type=relationship_type
        )

    def get_manif_inst_maps(self, manifestation_id: str = None,
                            institution_id: int = None) -> List[Dict]:
        """Get manifestation-institution relationships from cofk_manif_inst_map."""
        return self._get_many(
            "cofk_manif_inst_map",
            manif_id=manifestation_id,
            inst_id=institution_id
        )

    # ==================== UPDATE Methods ====================

    def _update(self, type_id: Any, field_updates: Dict, table_name: str,
                where_field: str, type_name: str, print_sql: bool = False,
                anonymous: bool = False):
        """Generic update method using SQLAlchemy."""
        self.check_database_connection()

        if not field_updates:
            return

        updates = dict(field_updates)
        if not anonymous and "change_user" not in updates:
            updates["change_user"] = self.user

        table = self._get_table(table_name)
        stmt = update(table).where(table.c[where_field] == type_id).values(**updates)

        if self.debug or print_sql:
            print(f"* UPDATE {type_name}:", stmt)

        self.connection.execute(stmt)
        self._audit_update(type_name)

    def update_person(self, person_id: str, field_updates: Dict = None,
                      print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(person_id, field_updates, "cofk_union_person",
                     "person_id", "person", print_sql, anonymous)

    def update_person_from_iperson(self, iperson_id: int, field_updates: Dict = None,
                                   print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(iperson_id, field_updates, "cofk_union_person",
                     "iperson_id", "person", print_sql, anonymous)

    def update_work(self, work_id: str, field_updates: Dict = None,
                    print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(work_id, field_updates, "cofk_union_work",
                     "work_id", "work", print_sql, anonymous)

    def update_work_from_iwork(self, iwork_id: int, field_updates: Dict = None,
                               print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(iwork_id, field_updates, "cofk_union_work",
                     "iwork_id", "work", print_sql, anonymous)

    def update_manifestation(self, manifestation_id: str, field_updates: Dict = None,
                             print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(manifestation_id, field_updates, "cofk_union_manifestation",
                     "manifestation_id", "manifestation", print_sql, anonymous)

    def update_comment(self, comment_id: int, field_updates: Dict = None,
                       print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(comment_id, field_updates, "cofk_union_comment",
                     "comment_id", "comment", print_sql, anonymous)

    def update_resource(self, resource_id: int, field_updates: Dict = None,
                        print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(resource_id, field_updates, "cofk_union_resource",
                     "resource_id", "resource", print_sql, anonymous)

    def update_institution(self, institution_id: int, field_updates: Dict = None,
                           print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(institution_id, field_updates, "cofk_union_institution",
                     "institution_id", "institution", print_sql, anonymous)

    def update_image(self, image_id: int, field_updates: Dict = None,
                     print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(image_id, field_updates, "cofk_union_image",
                     "image_id", "image", print_sql, anonymous)

    def update_location(self, location_id: int, field_updates: Dict = None,
                        print_sql: bool = False, anonymous: bool = False):
        field_updates = field_updates or {}
        self._update(location_id, field_updates, "cofk_union_location",
                     "location_id", "location", print_sql, anonymous)

    # ==================== DELETE Methods ====================

    def _delete_by_id(self, table_name: str, id_field: str, id_value: Any, audit_name: str):
        """Generic delete method using SQLAlchemy."""
        self.check_database_connection()
        table = self._get_table(table_name)
        stmt = delete(table).where(table.c[id_field] == id_value)
        self._print_command(f"DELETE {audit_name}", stmt)
        self._audit_delete(audit_name)
        self.connection.execute(stmt)

    def delete_resource_via_resource_id(self, resource_id: int):
        self._delete_by_id("cofk_union_resource", "resource_id", resource_id, "resource")

    def delete_comment_via_comment_id(self, comment_id: int):
        self._delete_by_id("cofk_union_comment", "comment_id", comment_id, "comment")

    def delete_manifestation_via_manifestation_id(self, manifestation_id: str):
        self._delete_by_id("cofk_union_manifestation", "manifestation_id", manifestation_id, "manifestation")

    def delete_work_via_iwork_id(self, iwork_id: int):
        self._delete_by_id("cofk_union_work", "iwork_id", int(iwork_id), "work")

    def delete_work_via_work_id(self, work_id: str):
        self._delete_by_id("cofk_union_work", "work_id", work_id, "work")

    # ==================== DELETE Mapping Tables ====================

    def delete_work_person_map(self, recref_id: int):
        self._delete_by_id("cofk_work_person_map", "recref_id", recref_id, "work_person_map")

    def delete_work_location_map(self, recref_id: int):
        self._delete_by_id("cofk_work_location_map", "recref_id", recref_id, "work_location_map")

    def delete_work_comment_map(self, recref_id: int):
        self._delete_by_id("cofk_work_comment_map", "recref_id", recref_id, "work_comment_map")

    def delete_work_resource_map(self, recref_id: int):
        self._delete_by_id("cofk_work_resource_map", "recref_id", recref_id, "work_resource_map")

    def delete_work_work_map(self, recref_id: int):
        self._delete_by_id("cofk_work_work_map", "recref_id", recref_id, "work_work_map")

    def delete_manif_inst_map(self, recref_id: int):
        self._delete_by_id("cofk_manif_inst_map", "recref_id", recref_id, "manif_inst_map")

    def delete_manif_image_map(self, recref_id: int):
        self._delete_by_id("cofk_manif_image_map", "recref_id", recref_id, "manif_image_map")

    def delete_person_comment_map(self, recref_id: int):
        self._delete_by_id("cofk_person_comment_map", "recref_id", recref_id, "person_comment_map")

    def delete_person_resource_map(self, recref_id: int):
        self._delete_by_id("cofk_person_resource_map", "recref_id", recref_id, "person_resource_map")

    def delete_person_location_map(self, recref_id: int):
        self._delete_by_id("cofk_person_location_map", "recref_id", recref_id, "person_location_map")

    # ==================== CREATE Methods ====================

    def _insert_returning(self, table_name: str, values: Dict, returning_field: str,
                          audit_name: str) -> Any:
        """Generic insert method that returns a field value."""
        self.check_database_connection()
        table = self._get_table(table_name)

        stmt = insert(table).values(**values).returning(table.c[returning_field])
        self._print_command(f"INSERT {audit_name}", stmt)
        self._audit_insert(audit_name)

        result = self.connection.execute(stmt)
        return result.fetchone()[0]

    def create_resource(self, name: str, url: str, description: str = "") -> int:
        return self._insert_returning(
            "cofk_union_resource",
            {
                "resource_name": name,
                "resource_url": url,
                "resource_details": description,
                "creation_user": self.user,
                "change_user": self.user
            },
            "resource_id",
            "resource"
        )

    def create_comment(self, comment: str) -> int:
        return self._insert_returning(
            "cofk_union_comment",
            {
                "comment": comment,
                "creation_user": self.user,
                "change_user": self.user
            },
            "comment_id",
            "comment"
        )

    def create_image(self, filename: str, display_order: int, image_credits: str,
                     can_be_displayed: str = 'Y', thumbnail: str = None,
                     licence_details: str = '', licence_url: str = '') -> int:
        return self._insert_returning(
            "cofk_union_image",
            {
                "image_filename": filename,
                "display_order": display_order,
                "credits": image_credits,
                "can_be_displayed": can_be_displayed,
                "thumbnail": thumbnail,
                "licence_details": licence_details,
                "licence_url": licence_url,
                "creation_user": self.user,
                "change_user": self.user
            },
            "image_id",
            "image"
        )

    def create_manifestation(
            self,
            manifestation_id: str,
            manifestation_type: str,
            work_id: str = None,
            printed_edition_details: str = None,
            id_number_or_shelfmark: str = None,
            paper_size: str = None,
            paper_type_or_watermark: str = None,
            number_of_pages_of_document: int = None,
            number_of_pages_of_text: int = None,
            seal: str = None,
            postage_marks: str = None,
            endorsements: str = None,
            non_letter_enclosures: str = None,
            manifestation_creation_calendar: str = 'U',
            manifestation_creation_date: str = None,
            manifestation_creation_date_gregorian: str = None,
            manifestation_creation_date_year: int = None,
            manifestation_creation_date_month: int = None,
            manifestation_creation_date_day: int = None,
            manifestation_creation_date2_year: int = None,
            manifestation_creation_date2_month: int = None,
            manifestation_creation_date2_day: int = None,
            manifestation_creation_date_is_range: int = 0,
            manifestation_creation_date_inferred: int = 0,
            manifestation_creation_date_uncertain: int = 0,
            manifestation_creation_date_approx: int = 0,
            manifestation_creation_date_as_marked: str = None,
            manifestation_is_translation: int = 0,
            language_of_manifestation: str = None,
            address: str = None,
            manifestation_incipit: str = None,
            manifestation_excipit: str = None,
            manifestation_ps: str = None,
            opened: str = 'o',
            routing_mark_stamp: str = None,
            routing_mark_ms: str = None,
            handling_instructions: str = None,
            stored_folded: str = None,
            postage_costs_as_marked: str = None,
            postage_costs: str = None,
            non_delivery_reason: str = None,
            date_of_receipt_as_marked: str = None,
            manifestation_receipt_calendar: str = '',
            manifestation_receipt_date: str = None,
            manifestation_receipt_date_gregorian: str = None,
            manifestation_receipt_date_year: int = None,
            manifestation_receipt_date_month: int = None,
            manifestation_receipt_date_day: int = None,
            manifestation_receipt_date2_year: int = None,
            manifestation_receipt_date2_month: int = None,
            manifestation_receipt_date2_day: int = None,
            manifestation_receipt_date_is_range: int = 0,
            manifestation_receipt_date_inferred: int = 0,
            manifestation_receipt_date_uncertain: int = 0,
            manifestation_receipt_date_approx: int = 0,
            accompaniments: str = None
    ) -> str:
        values = {
            "manifestation_id": manifestation_id,
            "manifestation_type": manifestation_type,
            "work_id": work_id,
            "id_number_or_shelfmark": id_number_or_shelfmark,
            "printed_edition_details": printed_edition_details,
            "paper_size": paper_size,
            "paper_type_or_watermark": paper_type_or_watermark,
            "number_of_pages_of_document": number_of_pages_of_document,
            "number_of_pages_of_text": number_of_pages_of_text,
            "seal": seal,
            "postage_marks": postage_marks,
            "endorsements": endorsements,
            "non_letter_enclosures": non_letter_enclosures,
            "manifestation_creation_calendar": manifestation_creation_calendar,
            "manifestation_creation_date": manifestation_creation_date,
            "manifestation_creation_date_gregorian": manifestation_creation_date_gregorian,
            "manifestation_creation_date_year": manifestation_creation_date_year,
            "manifestation_creation_date_month": manifestation_creation_date_month,
            "manifestation_creation_date_day": manifestation_creation_date_day,
            "manifestation_creation_date2_year": manifestation_creation_date2_year,
            "manifestation_creation_date2_month": manifestation_creation_date2_month,
            "manifestation_creation_date2_day": manifestation_creation_date2_day,
            "manifestation_creation_date_is_range": manifestation_creation_date_is_range,
            "manifestation_creation_date_inferred": manifestation_creation_date_inferred,
            "manifestation_creation_date_uncertain": manifestation_creation_date_uncertain,
            "manifestation_creation_date_approx": manifestation_creation_date_approx,
            "manifestation_creation_date_as_marked": manifestation_creation_date_as_marked,
            "manifestation_is_translation": manifestation_is_translation,
            "language_of_manifestation": language_of_manifestation,
            "address": address,
            "manifestation_incipit": manifestation_incipit,
            "manifestation_excipit": manifestation_excipit,
            "manifestation_ps": manifestation_ps,
            "opened": opened,
            "routing_mark_stamp": routing_mark_stamp,
            "routing_mark_ms": routing_mark_ms,
            "handling_instructions": handling_instructions,
            "stored_folded": stored_folded,
            "postage_costs_as_marked": postage_costs_as_marked,
            "postage_costs": postage_costs,
            "non_delivery_reason": non_delivery_reason,
            "date_of_receipt_as_marked": date_of_receipt_as_marked,
            "manifestation_receipt_calendar": manifestation_receipt_calendar,
            "manifestation_receipt_date": manifestation_receipt_date,
            "manifestation_receipt_date_gregorian": manifestation_receipt_date_gregorian,
            "manifestation_receipt_date_year": manifestation_receipt_date_year,
            "manifestation_receipt_date_month": manifestation_receipt_date_month,
            "manifestation_receipt_date_day": manifestation_receipt_date_day,
            "manifestation_receipt_date2_year": manifestation_receipt_date2_year,
            "manifestation_receipt_date2_month": manifestation_receipt_date2_month,
            "manifestation_receipt_date2_day": manifestation_receipt_date2_day,
            "manifestation_receipt_date_is_range": manifestation_receipt_date_is_range,
            "manifestation_receipt_date_inferred": manifestation_receipt_date_inferred,
            "manifestation_receipt_date_uncertain": manifestation_receipt_date_uncertain,
            "manifestation_receipt_date_approx": manifestation_receipt_date_approx,
            "accompaniments": accompaniments,
            "creation_user": self.user,
            "change_user": self.user
        }

        return self._insert_returning(
            "cofk_union_manifestation",
            values,
            "manifestation_id",
            "manifestation"
        )

    # ==================== CREATE Mapping Table Entries ====================

    def _create_map_entry(self, table_name: str, values: Dict,
                          relationship_type: str, audit_name: str,
                          skip_duplicate_check: bool = False) -> int:
        """Generic method to create mapping table entries.

        Validates relationship_type against VALID_RELATIONSHIP_TYPES and
        checks for duplicate relationships before inserting.

        Args:
            skip_duplicate_check: If True, bypass the duplicate detection check.
        """
        # Validate relationship type
        valid_types = VALID_RELATIONSHIP_TYPES.get(table_name)
        if valid_types is not None and relationship_type not in valid_types:
            raise InvalidRelationshipTypeError(
                f"Invalid relationship_type '{relationship_type}' for table '{table_name}'. "
                f"Valid types: {sorted(valid_types)}"
            )

        # Check for duplicates
        if not skip_duplicate_check:
            self.check_database_connection()
            table = self._get_table(table_name)
            stmt = select(table.c.recref_id)
            for col, val in values.items():
                stmt = stmt.where(table.c[col] == val)
            stmt = stmt.where(table.c.relationship_type == relationship_type)

            result = self.connection.execute(stmt)
            existing = result.fetchone()
            if existing:
                raise DuplicateRelationshipError(
                    f"Duplicate relationship in '{table_name}': a row with "
                    f"{values} and relationship_type='{relationship_type}' "
                    f"already exists (recref_id={existing[0]})"
                )

        values["relationship_type"] = relationship_type
        values["creation_user"] = self.user
        values["change_user"] = self.user

        return self._insert_returning(table_name, values, "recref_id", audit_name)

    # Work-Person relationships
    def create_work_person_map(self, work_id: str, person_id: str,
                                relationship_type: str) -> int:
        return self._create_map_entry(
            "cofk_work_person_map",
            {"work_id": work_id, "person_id": person_id},
            relationship_type,
            "work_person_map"
        )

    def create_relationship_created(self, person_id: str, work_id: str) -> int:
        """Author/creator relationship."""
        return self.create_work_person_map(work_id, person_id, REL_TYPE_CREATED)

    def create_relationship_addressed_to(self, work_id: str, person_id: str) -> int:
        """Addressee relationship."""
        return self.create_work_person_map(work_id, person_id, REL_TYPE_WAS_ADDRESSED_TO)

    def create_relationship_mentions(self, work_id: str, person_id: str) -> int:
        """Work mentions person."""
        return self.create_work_person_map(work_id, person_id, REL_TYPE_MENTION)

    def create_relationship_signed(self, work_id: str, person_id: str) -> int:
        """Person signed work."""
        return self.create_work_person_map(work_id, person_id, REL_TYPE_SIGNED)

    def create_relationship_sent(self, work_id: str, person_id: str) -> int:
        """Person sent work."""
        return self.create_work_person_map(work_id, person_id, REL_TYPE_SENT)

    def create_relationship_intended_for(self, work_id: str, person_id: str) -> int:
        """Work intended for person."""
        return self.create_work_person_map(work_id, person_id, REL_TYPE_INTENDED_FOR)

    # Work-Location relationships
    def create_work_location_map(self, work_id: str, location_id: int,
                                  relationship_type: str) -> int:
        return self._create_map_entry(
            "cofk_work_location_map",
            {"work_id": work_id, "location_id": location_id},
            relationship_type,
            "work_location_map"
        )

    def create_relationship_was_sent_to(self, work_id: str, location_id: int) -> int:
        """Destination."""
        return self.create_work_location_map(work_id, location_id, REL_TYPE_WAS_SENT_TO)

    def create_relationship_was_sent_from(self, work_id: str, location_id: int) -> int:
        """Origin."""
        return self.create_work_location_map(work_id, location_id, REL_TYPE_WAS_SENT_FROM)

    def create_relationship_mentions_place(self, work_id: str, location_id: int) -> int:
        """Work mentions place."""
        return self.create_work_location_map(work_id, location_id, REL_TYPE_MENTION_PLACE)

    # Work-Comment relationships
    def create_work_comment_map(self, work_id: str, comment_id: int,
                                 relationship_type: str) -> int:
        return self._create_map_entry(
            "cofk_work_comment_map",
            {"work_id": work_id, "comment_id": comment_id},
            relationship_type,
            "work_comment_map"
        )

    def create_relationship_note_on_work_route(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_ROUTE)

    def create_relationship_note_on_work_date(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_DATE)

    def create_relationship_note_on_work_author(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_AUTHOR)

    def create_relationship_note_on_work_origin(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_ORIGIN)

    def create_relationship_note_on_work_destination(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_DESTINATION)

    def create_relationship_note_on_work_generally(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_REFERS_TO)

    def create_relationship_note_on_work_people_mentioned(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_PERSON_MENTIONED)

    def create_relationship_note_on_work_addressee(self, comment_id: int, work_id: str) -> int:
        return self.create_work_comment_map(work_id, comment_id, REL_TYPE_COMMENT_ADDRESSEE)

    # Work-Resource relationships
    def create_work_resource_map(self, work_id: str, resource_id: int) -> int:
        return self._create_map_entry(
            "cofk_work_resource_map",
            {"work_id": work_id, "resource_id": resource_id},
            REL_TYPE_IS_RELATED_TO,
            "work_resource_map"
        )

    def create_relationship_work_resource(self, work_id: str, resource_id: int) -> int:
        return self.create_work_resource_map(work_id, resource_id)

    # Work-Work relationships
    def create_work_work_map(self, work_from_id: str, work_to_id: str,
                              relationship_type: str) -> int:
        return self._create_map_entry(
            "cofk_work_work_map",
            {"work_from_id": work_from_id, "work_to_id": work_to_id},
            relationship_type,
            "work_work_map"
        )

    def create_relationship_work_reply_to(self, work_reply_id: str, work_id: str) -> int:
        return self.create_work_work_map(work_reply_id, work_id, REL_TYPE_WORK_IS_REPLY_TO)

    def create_relationship_work_matches(self, work_id_1: str, work_id_2: str) -> int:
        return self.create_work_work_map(work_id_1, work_id_2, REL_TYPE_WORK_MATCHES)

    # Person-Comment relationships
    def create_person_comment_map(self, person_id: str, comment_id: int,
                                   relationship_type: str = REL_TYPE_COMMENT_REFERS_TO) -> int:
        return self._create_map_entry(
            "cofk_person_comment_map",
            {"person_id": person_id, "comment_id": comment_id},
            relationship_type,
            "person_comment_map"
        )

    def create_relationship_note_on_person(self, comment_id: int, person_id: str) -> int:
        return self.create_person_comment_map(person_id, comment_id, REL_TYPE_COMMENT_REFERS_TO)

    # Person-Resource relationships
    def create_person_resource_map(self, person_id: str, resource_id: int) -> int:
        return self._create_map_entry(
            "cofk_person_resource_map",
            {"person_id": person_id, "resource_id": resource_id},
            REL_TYPE_IS_RELATED_TO,
            "person_resource_map"
        )

    def create_relationship_person_resource(self, person_id: str, resource_id: int) -> int:
        return self.create_person_resource_map(person_id, resource_id)

    # Person-Location relationships
    def create_person_location_map(self, person_id: str, location_id: int,
                                    relationship_type: str) -> int:
        return self._create_map_entry(
            "cofk_person_location_map",
            {"person_id": person_id, "location_id": location_id},
            relationship_type,
            "person_location_map"
        )

    def create_relationship_person_born_in(self, person_id: str, location_id: int) -> int:
        return self.create_person_location_map(person_id, location_id, REL_TYPE_WAS_BORN_IN_LOCATION)

    def create_relationship_person_died_at(self, person_id: str, location_id: int) -> int:
        return self.create_person_location_map(person_id, location_id, REL_TYPE_DIED_AT_LOCATION)

    def create_relationship_person_was_in(self, person_id: str, location_id: int) -> int:
        return self.create_person_location_map(person_id, location_id, REL_TYPE_WAS_IN_LOCATION)

    # Manifestation-Comment relationships
    def create_manif_comment_map(self, manifestation_id: str, comment_id: int,
                                  relationship_type: str = REL_TYPE_COMMENT_REFERS_TO) -> int:
        return self._create_map_entry(
            "cofk_manif_comment_map",
            {"manifestation_id": manifestation_id, "comment_id": comment_id},
            relationship_type,
            "manif_comment_map"
        )

    def create_relationship_note_manifestation(self, comment_id: int, manifestation_id: str) -> int:
        return self.create_manif_comment_map(manifestation_id, comment_id, REL_TYPE_COMMENT_REFERS_TO)

    # Manifestation-Institution relationships
    def create_manif_inst_map(self, manifestation_id: str, institution_id: int,
                               relationship_type: str = REL_TYPE_STORED_IN) -> int:
        return self._create_map_entry(
            "cofk_manif_inst_map",
            {"manif_id": manifestation_id, "inst_id": institution_id},
            relationship_type,
            "manif_inst_map"
        )

    def create_relationship_manifestation_of_work(self, manifestation_id: str,
                                                      work_id: str):
        """Link manifestation to work via the work_id column."""
        self.update_manifestation(manifestation_id, {"work_id": work_id})

    def create_relationship_manifestation_in_repository(self, manifestation_id: str,
                                                         repository_id: int) -> int:
        return self.create_manif_inst_map(manifestation_id, repository_id, REL_TYPE_STORED_IN)

    # ==================== CREATE Work ====================

    def create_work(
            self,
            work_id_end: str,
            abstract: str = None,
            accession_code: str = None,
            addressees_as_marked: str = None,
            addressees_inferred: int = 0,
            addressees_uncertain: int = 0,
            authors_as_marked: str = None,
            authors_inferred: int = 0,
            authors_uncertain: int = 0,
            date_of_work2_std_day: int = None,
            date_of_work2_std_month: int = None,
            date_of_work2_std_year: int = None,
            date_of_work_approx: int = 0,
            date_of_work_as_marked: str = None,
            date_of_work_inferred: int = 0,
            date_of_work_std_day: int = None,
            date_of_work_std_is_range: int = 0,
            date_of_work_std_month: int = None,
            date_of_work_std_year: int = None,
            date_of_work_uncertain: int = 0,
            description: str = None,
            destination_as_marked: str = None,
            destination_inferred: int = 0,
            destination_uncertain: int = 0,
            edit_status: str = '',
            editors_notes: str = None,
            explicit: str = None,
            incipit: str = None,
            keywords: str = None,
            origin_as_marked: str = None,
            origin_inferred: int = 0,
            origin_uncertain: int = 0,
            original_calendar: str = '',
            original_catalogue: str = '',
            ps: str = None,
            relevant_to_cofk: str = 'Y',
            work_is_translation: int = 0,
            work_to_be_deleted: int = 0
    ) -> str:
        self.check_database_connection()

        # Generate work_id
        work_id_base = "work_" + datetime.strftime(datetime.now(), "%Y%m%d%H%M%S%f") + "_"
        work_id = work_id_base + work_id_end

        # Get next iwork_id using SQLAlchemy
        result = self.connection.execute(text("SELECT nextval('cofk_union_work_iwork_id_seq'::regclass)"))
        iwork_id = result.fetchone()[0]

        # Convert values
        addressees_inferred = self.get_int_value(addressees_inferred, 0)
        addressees_uncertain = self.get_int_value(addressees_uncertain, 0)
        authors_inferred = self.get_int_value(authors_inferred, 0)
        authors_uncertain = self.get_int_value(authors_uncertain, 0)
        date_of_work2_std_day = self.get_int_value(date_of_work2_std_day)
        date_of_work2_std_month = self.get_int_value(date_of_work2_std_month)
        date_of_work2_std_year = self.get_int_value(date_of_work2_std_year)
        date_of_work_std_day = self.get_int_value(date_of_work_std_day)
        date_of_work_std_month = self.get_int_value(date_of_work_std_month)
        date_of_work_std_year = self.get_int_value(date_of_work_std_year)
        date_of_work_approx = self.get_int_value(date_of_work_approx, 0)
        date_of_work_inferred = self.get_int_value(date_of_work_inferred, 0)
        date_of_work_std_is_range = self.get_int_value(date_of_work_std_is_range, 0)
        date_of_work_uncertain = self.get_int_value(date_of_work_uncertain, 0)
        destination_inferred = self.get_int_value(destination_inferred, 0)
        destination_uncertain = self.get_int_value(destination_uncertain, 0)
        origin_inferred = self.get_int_value(origin_inferred, 0)
        origin_uncertain = self.get_int_value(origin_uncertain, 0)
        work_is_translation = self.get_int_value(work_is_translation, 0)
        work_to_be_deleted = self.get_int_value(work_to_be_deleted, 0)

        date_of_work_std = self.get_date_string(date_of_work_std_year, date_of_work_std_month, date_of_work_std_day)
        date_of_work_std_gregorian = date_of_work_std

        values = {
            "work_id": work_id,
            "iwork_id": iwork_id,
            "description": description,
            "date_of_work_as_marked": date_of_work_as_marked,
            "original_calendar": original_calendar,
            "date_of_work_std": date_of_work_std,
            "date_of_work_std_gregorian": date_of_work_std_gregorian,
            "date_of_work_std_year": date_of_work_std_year,
            "date_of_work_std_month": date_of_work_std_month,
            "date_of_work_std_day": date_of_work_std_day,
            "date_of_work2_std_year": date_of_work2_std_year,
            "date_of_work2_std_month": date_of_work2_std_month,
            "date_of_work2_std_day": date_of_work2_std_day,
            "date_of_work_std_is_range": date_of_work_std_is_range,
            "date_of_work_inferred": date_of_work_inferred,
            "date_of_work_uncertain": date_of_work_uncertain,
            "date_of_work_approx": date_of_work_approx,
            "authors_as_marked": authors_as_marked,
            "addressees_as_marked": addressees_as_marked,
            "authors_inferred": authors_inferred,
            "authors_uncertain": authors_uncertain,
            "addressees_inferred": addressees_inferred,
            "addressees_uncertain": addressees_uncertain,
            "destination_as_marked": destination_as_marked,
            "origin_as_marked": origin_as_marked,
            "destination_inferred": destination_inferred,
            "destination_uncertain": destination_uncertain,
            "origin_inferred": origin_inferred,
            "origin_uncertain": origin_uncertain,
            "abstract": abstract,
            "keywords": keywords,
            "work_is_translation": work_is_translation,
            "incipit": incipit,
            "explicit": explicit,
            "ps": ps,
            "original_catalogue": original_catalogue,
            "accession_code": accession_code,
            "work_to_be_deleted": work_to_be_deleted,
            "editors_notes": editors_notes,
            "edit_status": edit_status,
            "relevant_to_cofk": relevant_to_cofk,
            "creation_user": self.user,
            "change_user": self.user
        }

        table = self._get_table("cofk_union_work")
        stmt = insert(table).values(**values)
        self._print_command("CREATE work", stmt)
        self._audit_insert("work")
        self.connection.execute(stmt)

        return work_id

    # ==================== CREATE Person ====================

    def create_person_or_organisation(
            self,
            primary_name: str,
            synonyms: str = None,
            aliases: str = None,
            gender: str = '',
            is_org: str = '',
            org_type: int = None,
            birth_year: int = None,
            birth_month: int = None,
            birth_day: int = None,
            birth_inferred: int = 0,
            birth_uncertain: int = 0,
            birth_approx: int = 0,
            birth_calendar: str = '',
            birth_is_range: int = 0,
            birth2_year: int = None,
            birth2_month: int = None,
            birth2_day: int = None,
            death_year: int = None,
            death_month: int = None,
            death_day: int = None,
            death_inferred: int = 0,
            death_uncertain: int = 0,
            death_approx: int = 0,
            death_calendar: str = '',
            death_is_range: int = 0,
            death2_year: int = None,
            death2_month: int = None,
            death2_day: int = None,
            flourished_year: int = None,
            flourished_month: int = None,
            flourished_day: int = None,
            flourished2_year: int = None,
            flourished2_month: int = None,
            flourished2_day: int = None,
            flourished_is_range: int = 0,
            flourished_calendar: str = '',
            flourished_inferred: int = 0,
            flourished_uncertain: int = 0,
            flourished_approx: int = 0,
            editors_notes: str = '',
            further_reading: str = None,
            skos_hiddenlabel: str = None
    ) -> str:
        self.check_database_connection()

        # Convert integer values
        birth_year = self.get_int_value(birth_year)
        birth_month = self.get_int_value(birth_month)
        birth_day = self.get_int_value(birth_day)
        birth_approx = self.get_int_value(birth_approx, 0)
        birth_inferred = self.get_int_value(birth_inferred, 0)
        birth_uncertain = self.get_int_value(birth_uncertain, 0)
        birth_is_range = self.get_int_value(birth_is_range, 0)
        birth2_year = self.get_int_value(birth2_year)
        birth2_month = self.get_int_value(birth2_month)
        birth2_day = self.get_int_value(birth2_day)

        death_year = self.get_int_value(death_year)
        death_month = self.get_int_value(death_month)
        death_day = self.get_int_value(death_day)
        death_approx = self.get_int_value(death_approx, 0)
        death_inferred = self.get_int_value(death_inferred, 0)
        death_uncertain = self.get_int_value(death_uncertain, 0)
        death_is_range = self.get_int_value(death_is_range, 0)
        death2_year = self.get_int_value(death2_year)
        death2_month = self.get_int_value(death2_month)
        death2_day = self.get_int_value(death2_day)

        flourished_year = self.get_int_value(flourished_year)
        flourished_month = self.get_int_value(flourished_month)
        flourished_day = self.get_int_value(flourished_day)
        flourished2_year = self.get_int_value(flourished2_year)
        flourished2_month = self.get_int_value(flourished2_month)
        flourished2_day = self.get_int_value(flourished2_day)
        flourished_is_range = self.get_int_value(flourished_is_range, 0)
        flourished_inferred = self.get_int_value(flourished_inferred, 0)
        flourished_uncertain = self.get_int_value(flourished_uncertain, 0)
        flourished_approx = self.get_int_value(flourished_approx, 0)

        # Handle is_org
        if is_org in (1, '1', 'Y', 'y'):
            is_org = 'Y'
        else:
            is_org = ''

        if is_org == 'Y':
            org_type = self.get_int_value(org_type)
        if org_type == '':
            org_type = None

        # Build date strings
        date_of_birth = None
        if birth_year or birth_month or birth_day:
            date_of_birth = self.get_date_string(birth_year, birth_month, birth_day)

        date_of_death = None
        if death_year or death_month or death_day:
            date_of_death = self.get_date_string(death_year, death_month, death_day)

        flourished = None
        if flourished_year or flourished_month or flourished_day:
            flourished = self.get_date_string(flourished_year, flourished_month, flourished_day)

        # Handle synonyms and aliases
        if synonyms:
            synonyms = "; ".join(synonyms.split("\n"))
        if aliases:
            aliases = "; ".join(aliases.split("\n"))

        # Handle gender
        if gender in ('m', 'M'):
            gender = 'M'
        elif gender in ('f', 'F'):
            gender = 'F'
        else:
            gender = ''

        # Get next available ID
        result = self.connection.execute(text("SELECT nextval('cofk_union_person_iperson_id_seq'::regclass)"))
        iperson_id = result.fetchone()[0]
        person_id = f"cofk_union_person-iperson_id:{iperson_id:06d}"

        values = {
            "person_id": person_id,
            "iperson_id": iperson_id,
            "foaf_name": primary_name,
            "skos_altlabel": synonyms,
            "skos_hiddenlabel": skos_hiddenlabel,
            "person_aliases": aliases,
            "date_of_birth_year": birth_year,
            "date_of_birth_month": birth_month,
            "date_of_birth_day": birth_day,
            "date_of_birth": date_of_birth,
            "date_of_birth_inferred": birth_inferred,
            "date_of_birth_uncertain": birth_uncertain,
            "date_of_birth_approx": birth_approx,
            "date_of_birth_calendar": birth_calendar,
            "date_of_birth_is_range": birth_is_range,
            "date_of_birth2_year": birth2_year,
            "date_of_birth2_month": birth2_month,
            "date_of_birth2_day": birth2_day,
            "date_of_death_year": death_year,
            "date_of_death_month": death_month,
            "date_of_death_day": death_day,
            "date_of_death": date_of_death,
            "date_of_death_inferred": death_inferred,
            "date_of_death_uncertain": death_uncertain,
            "date_of_death_approx": death_approx,
            "date_of_death_calendar": death_calendar,
            "date_of_death_is_range": death_is_range,
            "date_of_death2_year": death2_year,
            "date_of_death2_month": death2_month,
            "date_of_death2_day": death2_day,
            "gender": gender,
            "is_organisation": is_org,
            "organisation_type": org_type,
            "flourished_year": flourished_year,
            "flourished_month": flourished_month,
            "flourished_day": flourished_day,
            "flourished": flourished,
            "flourished2_year": flourished2_year,
            "flourished2_month": flourished2_month,
            "flourished2_day": flourished2_day,
            "flourished_is_range": flourished_is_range,
            "flourished_calendar": flourished_calendar,
            "flourished_inferred": flourished_inferred,
            "flourished_uncertain": flourished_uncertain,
            "flourished_approx": flourished_approx,
            "editors_notes": editors_notes,
            "further_reading": further_reading,
            "creation_user": self.user,
            "change_user": self.user
        }

        return self._insert_returning(
            "cofk_union_person",
            values,
            "person_id",
            "person"
        )

    # ==================== CREATE Location ====================

    def create_location(
            self,
            latitude: str = None,
            longitude: str = None,
            location_synonyms: str = None,
            editors_notes: str = None,
            element_1_eg_room: str = '',
            element_2_eg_building: str = '',
            element_3_eg_parish: str = '',
            element_4_eg_city: str = '',
            element_5_eg_county: str = '',
            element_6_eg_country: str = '',
            element_7_eg_empire: str = ''
    ) -> int:
        location_list = []
        for value in [element_1_eg_room, element_2_eg_building, element_3_eg_parish,
                      element_4_eg_city, element_5_eg_county, element_6_eg_country,
                      element_7_eg_empire]:
            if value:
                location_list.append(value)

        location_name = ", ".join(location_list)

        return self._insert_returning(
            "cofk_union_location",
            {
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "location_synonyms": location_synonyms,
                "element_1_eg_room": element_1_eg_room,
                "element_2_eg_building": element_2_eg_building,
                "element_3_eg_parish": element_3_eg_parish,
                "element_4_eg_city": element_4_eg_city,
                "element_5_eg_county": element_5_eg_county,
                "element_6_eg_country": element_6_eg_country,
                "element_7_eg_empire": element_7_eg_empire,
                "editors_notes": editors_notes,
                "creation_user": self.user,
                "change_user": self.user
            },
            "location_id",
            "location"
        )

    # ==================== Language Utilities ====================

    def get_languages_from_code(self, code: str) -> str:
        """Get language names from ISO 639-3 codes (semicolon-separated)."""
        self.check_database_connection()

        codes = code.split(";")
        table = self._get_table("iso_639_language_codes")

        stmt = select(table.c.language_name).where(table.c.code_639_3.in_(codes))
        result = self.connection.execute(stmt)

        languages = [row[0] for row in result]
        return ", ".join(languages)

    def add_language_to_work(self, work_id: str, language_code: str, notes: str = None):
        """Add a language to a work via cofk_union_language_of_work."""
        self.check_database_connection()

        # Use text() for ON CONFLICT which is PostgreSQL-specific
        stmt = text("""
            INSERT INTO cofk_union_language_of_work (work_id, language_code, notes)
            VALUES (:work_id, :language_code, :notes)
            ON CONFLICT (work_id, language_code) DO NOTHING
        """)

        self._print_command("INSERT language_of_work", stmt)
        self.connection.execute(stmt, {"work_id": work_id, "language_code": language_code, "notes": notes})
        self._audit_insert("language_of_work")

    def add_language_to_manifestation(self, manifestation_id: str, language_code: str,
                                       notes: str = None):
        """Add a language to a manifestation via cofk_union_language_of_manifestation."""
        self.check_database_connection()

        stmt = text("""
            INSERT INTO cofk_union_language_of_manifestation (manifestation_id, language_code, notes)
            VALUES (:manifestation_id, :language_code, :notes)
            ON CONFLICT (manifestation_id, language_code) DO NOTHING
        """)

        self._print_command("INSERT language_of_manifestation", stmt)
        self.connection.execute(stmt, {"manifestation_id": manifestation_id,
                                        "language_code": language_code, "notes": notes})
        self._audit_insert("language_of_manifestation")

    # ==================== Utility Methods ====================

    @staticmethod
    def get_int_value(value, default: int = None) -> Optional[int]:
        if value is not None and value != '':
            if isinstance(value, str) and value.upper() in ('Y', 'N'):
                return 1 if value.upper() == 'Y' else 0
            return int(value)
        return default

    @staticmethod
    def get_date_string(year: int = None, month: int = None, day: int = None) -> str:
        year = int(year) if year is not None else 9999
        month = int(month) if month is not None else 12

        if day is None:
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day = 31
            elif month == 2:
                day = 28
            else:
                day = 30

        return f"{year:04d}-{month:02d}-{day:02d}"

    def calendar_julian_to_calendar_gregorian(self, day: int, month: int, year: int) -> Dict:
        """Convert Julian calendar date to Gregorian."""
        max_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if year % 4 == 0:
            max_month[1] = 29

        diff_days = 10
        if year > 1700:
            diff_days = 11
        elif year == 1700 and month > 2:
            diff_days = 11
        elif year == 1700 and month == 2 and day == 29:
            diff_days = 11

        new_day = day + diff_days
        new_month = month
        new_year = year
        if new_day > max_month[month - 1]:
            new_day = new_day % max_month[month - 1]
            new_month += 1
            if new_month > 12:
                new_month = 1
                new_year += 1

        return {"d": new_day, "m": new_month, "y": new_year}

    # ==================== Transaction Methods ====================

    def commit_changes(self, commit: bool = False, quiet: bool = False):
        """Commit or rollback changes."""
        self.check_database_connection()

        if commit:
            self.connection.commit()
        else:
            self.connection.rollback()
            self._reset_audit()

        if not quiet:
            if commit:
                print("Committing... Done.")
            else:
                print("NOT committing... Rolled back.")

    def check_database_connection(self):
        if not self.database_ok():
            raise SQLAlchemyError("Database not connected")

    def database_ok(self) -> bool:
        return bool(self.engine and self.connection)

    # ==================== Audit Methods ====================

    def print_audit(self, going_to_commit: bool = True):
        print("Audit:")

        for deleting, number in self.audit["deletions"].items():
            if going_to_commit:
                print(f"- Deleting {number} {deleting}(s)")
            else:
                print(f"- I would have deleted {number} {deleting}(s)")

        if not self.audit["deletions"]:
            print("- Nothing to delete")

        for inserting, number in self.audit["insertions"].items():
            if going_to_commit:
                print(f"- Inserting {number} {inserting}(s)")
            else:
                print(f"- I would have inserted {number} {inserting}(s)")

        if not self.audit["insertions"]:
            print("- Nothing to insert")

        for updating, number in self.audit["updates"].items():
            if going_to_commit:
                print(f"- Updating {number} {updating}(s)")
            else:
                print(f"- I would have updated {number} {updating}(s)")

        if not self.audit["updates"]:
            print("- Nothing to update")

        if not going_to_commit:
            print("- Not committing changes.")

    def _audit_update(self, updated: str):
        self.audit["updates"][updated] = self.audit["updates"].get(updated, 0) + 1

    def _audit_delete(self, deleted: str):
        self.audit["deletions"][deleted] = self.audit["deletions"].get(deleted, 0) + 1

    def _audit_insert(self, inserted: str):
        self.audit["insertions"][inserted] = self.audit["insertions"].get(inserted, 0) + 1

    def _print_command(self, name: str, stmt):
        if self.debug:
            print(f" * {name}:", stmt)

    # ==================== Trigger Methods ====================

    def triggers_enable(self, table_name: str, triggers: List[str] = None):
        triggers = triggers or []
        if not triggers:
            return

        for trigger in triggers:
            stmt = text(f"ALTER TABLE {table_name} ENABLE TRIGGER {trigger}")
            self._print_command("ENABLE Trigger", stmt)
            self.connection.execute(stmt)

    def triggers_disable(self, table_name: str, triggers: List[str] = None):
        triggers = triggers or []
        if not triggers:
            return

        for trigger in triggers:
            stmt = text(f"ALTER TABLE {table_name} DISABLE TRIGGER {trigger}")
            self._print_command("DISABLE Trigger", stmt)
            self.connection.execute(stmt)

    # ==================== Raw SQL Execution ====================

    def execute_raw(self, sql: str, params: Dict = None) -> List[Dict]:
        """Execute raw SQL and return results as list of dicts."""
        self.check_database_connection()
        stmt = text(sql)
        self._print_command("RAW SQL", stmt)
        result = self.connection.execute(stmt, params or {})

        try:
            return [dict(row._mapping) for row in result]
        except ResourceClosedError:
            return []

    def execute_scalar(self, sql: str, params: Dict = None) -> Any:
        """Execute raw SQL and return a single scalar value."""
        self.check_database_connection()
        stmt = text(sql)
        self._print_command("RAW SQL", stmt)
        try:
            result = self.connection.execute(stmt, params or {})
            row = result.fetchone()
            return row[0] if row else None
        except SQLAlchemyError as e:
            raise SQLAlchemyError(
                f"execute_scalar failed on SQL: {sql}"
            ) from e
