# -*- coding: utf-8 -*-
"""
Database tweaker for EMLO/CofK database operations.
Synced with site-edit-2 Django models.
"""
import sys
import csv
from datetime import datetime
from typing import Optional, Dict, Any, List

import psycopg2
import psycopg2.extras

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


class DatabaseTweaker:
    """
    Database tweaker for CofK/EMLO PostgreSQL database operations.

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
        postgres_connection = (
            f"dbname='{dbname}' host='{host}' port='{port}' "
            f"user='{user}' password='{password}'"
        )
        return cls(postgres_connection, debug)

    def __init__(self, connection: Optional[str] = None, debug: bool = False):
        self.debug = False
        self.set_debug(debug)

        self.connection = self.cursor = None
        if connection:
            self.connect_to_postgres(connection)

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

    def connect_to_postgres(self, connection: str):
        try:
            self.connection = psycopg2.connect(connection)
        except psycopg2.Error as e:
            print(f"ERROR: Unable to connect to the database: {e}")
            sys.exit(1)
        else:
            if self.debug:
                print("Connected to database...")
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Alias for backwards compatibility
    connect_to_postres = connect_to_postgres

    def close(self):
        if self.connection:
            self.connection.close()
        self.connection = self.cursor = None

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

    def get_work_from_iwork_id(self, iwork_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_work WHERE iwork_id=%s"
        command = self.cursor.mogrify(command, (int(iwork_id),))
        self._print_command("SELECT work", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_work_from_work_id(self, work_id: str):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_work WHERE work_id=%s"
        command = self.cursor.mogrify(command, (work_id,))
        self._print_command("SELECT work", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_resource_from_resource_id(self, resource_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_resource WHERE resource_id=%s"
        command = self.cursor.mogrify(command, (resource_id,))
        self._print_command("SELECT resource", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_image_from_image_id(self, image_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_image WHERE image_id=%s"
        command = self.cursor.mogrify(command, (image_id,))
        self._print_command("SELECT image", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_comment_from_comment_id(self, comment_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_comment WHERE comment_id=%s"
        command = self.cursor.mogrify(command, (comment_id,))
        self._print_command("SELECT comment", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_institution_from_institution_id(self, institution_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_institution WHERE institution_id=%s"
        command = self.cursor.mogrify(command, (institution_id,))
        self._print_command("SELECT institution", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_location_from_location_id(self, location_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_location WHERE location_id=%s"
        command = self.cursor.mogrify(command, (location_id,))
        self._print_command("SELECT location", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_person_from_iperson_id(self, iperson_id: int):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_person WHERE iperson_id=%s"
        command = self.cursor.mogrify(command, (iperson_id,))
        self._print_command("SELECT person", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_person_from_person_id(self, person_id: str):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_person WHERE person_id=%s"
        command = self.cursor.mogrify(command, (person_id,))
        self._print_command("SELECT person", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    def get_manifestation_from_manifestation_id(self, manifestation_id: str):
        self.check_database_connection()
        command = "SELECT * FROM cofk_union_manifestation WHERE manifestation_id=%s"
        command = self.cursor.mogrify(command, (manifestation_id,))
        self._print_command("SELECT manifestation", command)
        self.cursor.execute(command)
        return self.cursor.fetchone()

    # ==================== Mapping Table Queries ====================

    def get_work_person_maps(self, work_id: str = None, person_id: str = None,
                             relationship_type: str = None) -> List[Dict]:
        """Get work-person relationships from cofk_work_person_map."""
        self.check_database_connection()

        conditions = []
        values = []

        if work_id:
            conditions.append("work_id=%s")
            values.append(work_id)
        if person_id:
            conditions.append("person_id=%s")
            values.append(person_id)
        if relationship_type:
            conditions.append("relationship_type=%s")
            values.append(relationship_type)

        command = "SELECT * FROM cofk_work_person_map"
        if conditions:
            command += " WHERE " + " AND ".join(conditions)

        command = self.cursor.mogrify(command, values)
        self._print_command("SELECT work_person_map", command)
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_work_location_maps(self, work_id: str = None, location_id: int = None,
                               relationship_type: str = None) -> List[Dict]:
        """Get work-location relationships from cofk_work_location_map."""
        self.check_database_connection()

        conditions = []
        values = []

        if work_id:
            conditions.append("work_id=%s")
            values.append(work_id)
        if location_id:
            conditions.append("location_id=%s")
            values.append(location_id)
        if relationship_type:
            conditions.append("relationship_type=%s")
            values.append(relationship_type)

        command = "SELECT * FROM cofk_work_location_map"
        if conditions:
            command += " WHERE " + " AND ".join(conditions)

        command = self.cursor.mogrify(command, values)
        self._print_command("SELECT work_location_map", command)
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_work_comment_maps(self, work_id: str = None, comment_id: int = None,
                              relationship_type: str = None) -> List[Dict]:
        """Get work-comment relationships from cofk_work_comment_map."""
        self.check_database_connection()

        conditions = []
        values = []

        if work_id:
            conditions.append("work_id=%s")
            values.append(work_id)
        if comment_id:
            conditions.append("comment_id=%s")
            values.append(comment_id)
        if relationship_type:
            conditions.append("relationship_type=%s")
            values.append(relationship_type)

        command = "SELECT * FROM cofk_work_comment_map"
        if conditions:
            command += " WHERE " + " AND ".join(conditions)

        command = self.cursor.mogrify(command, values)
        self._print_command("SELECT work_comment_map", command)
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_work_resource_maps(self, work_id: str = None, resource_id: int = None) -> List[Dict]:
        """Get work-resource relationships from cofk_work_resource_map."""
        self.check_database_connection()

        conditions = []
        values = []

        if work_id:
            conditions.append("work_id=%s")
            values.append(work_id)
        if resource_id:
            conditions.append("resource_id=%s")
            values.append(resource_id)

        command = "SELECT * FROM cofk_work_resource_map"
        if conditions:
            command += " WHERE " + " AND ".join(conditions)

        command = self.cursor.mogrify(command, values)
        self._print_command("SELECT work_resource_map", command)
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_work_work_maps(self, work_from_id: str = None, work_to_id: str = None,
                           relationship_type: str = None) -> List[Dict]:
        """Get work-work relationships from cofk_work_work_map."""
        self.check_database_connection()

        conditions = []
        values = []

        if work_from_id:
            conditions.append("work_from_id=%s")
            values.append(work_from_id)
        if work_to_id:
            conditions.append("work_to_id=%s")
            values.append(work_to_id)
        if relationship_type:
            conditions.append("relationship_type=%s")
            values.append(relationship_type)

        command = "SELECT * FROM cofk_work_work_map"
        if conditions:
            command += " WHERE " + " AND ".join(conditions)

        command = self.cursor.mogrify(command, values)
        self._print_command("SELECT work_work_map", command)
        self.cursor.execute(command)
        return self.cursor.fetchall()

    def get_manif_inst_maps(self, manifestation_id: str = None,
                            institution_id: int = None) -> List[Dict]:
        """Get manifestation-institution relationships from cofk_manif_inst_map."""
        self.check_database_connection()

        conditions = []
        values = []

        if manifestation_id:
            conditions.append("manif_id=%s")
            values.append(manifestation_id)
        if institution_id:
            conditions.append("inst_id=%s")
            values.append(institution_id)

        command = "SELECT * FROM cofk_manif_inst_map"
        if conditions:
            command += " WHERE " + " AND ".join(conditions)

        command = self.cursor.mogrify(command, values)
        self._print_command("SELECT manif_inst_map", command)
        self.cursor.execute(command)
        return self.cursor.fetchall()

    # ==================== UPDATE Methods ====================

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

    def _update(self, type_id, field_updates: Dict, update_table: str,
                where_field: str, type_name: str, print_sql: bool = False,
                anonymous: bool = False):
        self.check_database_connection()

        fields = list(field_updates.keys())
        data = [field_updates[field] for field in fields]

        if not anonymous and "change_user" not in fields:
            fields.append("change_user")
            data.append(self.user)

        data.append(type_id)

        command = f"UPDATE {update_table} SET "
        command += ", ".join(f"{field}=%s" for field in fields)
        command += f" WHERE {where_field}=%s"

        command = self.cursor.mogrify(command, data)

        if self.debug or print_sql:
            print(f"* UPDATE {type_name}:", command)

        self.cursor.execute(command)
        self._audit_update(type_name)

    # ==================== DELETE Methods ====================

    def delete_resource_via_resource_id(self, resource_id: int):
        self.check_database_connection()
        command = "DELETE FROM cofk_union_resource WHERE resource_id=%s"
        command = self.cursor.mogrify(command, (resource_id,))
        self._print_command("DELETE resource", command)
        self._audit_delete("resource")
        self.cursor.execute(command)

    def delete_comment_via_comment_id(self, comment_id: int):
        self.check_database_connection()
        command = "DELETE FROM cofk_union_comment WHERE comment_id=%s"
        command = self.cursor.mogrify(command, (comment_id,))
        self._print_command("DELETE comment", command)
        self._audit_delete("comment")
        self.cursor.execute(command)

    def delete_manifestation_via_manifestation_id(self, manifestation_id: str):
        self.check_database_connection()
        command = "DELETE FROM cofk_union_manifestation WHERE manifestation_id=%s"
        command = self.cursor.mogrify(command, (manifestation_id,))
        self._print_command("DELETE manifestation", command)
        self._audit_delete("manifestation")
        self.cursor.execute(command)

    def delete_work_via_iwork_id(self, iwork_id: int):
        self.check_database_connection()
        command = "DELETE FROM cofk_union_work WHERE iwork_id=%s"
        command = self.cursor.mogrify(command, (int(iwork_id),))
        self._print_command("DELETE work", command)
        self._audit_delete("work")
        self.cursor.execute(command)

    def delete_work_via_work_id(self, work_id: str):
        self.check_database_connection()
        command = "DELETE FROM cofk_union_work WHERE work_id=%s"
        command = self.cursor.mogrify(command, (work_id,))
        self._print_command("DELETE work", command)
        self._audit_delete("work")
        self.cursor.execute(command)

    # ==================== DELETE Mapping Tables ====================

    def delete_work_person_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_work_person_map", recref_id, "work_person_map")

    def delete_work_location_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_work_location_map", recref_id, "work_location_map")

    def delete_work_comment_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_work_comment_map", recref_id, "work_comment_map")

    def delete_work_resource_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_work_resource_map", recref_id, "work_resource_map")

    def delete_work_work_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_work_work_map", recref_id, "work_work_map")

    def delete_manif_inst_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_manif_inst_map", recref_id, "manif_inst_map")

    def delete_manif_image_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_manif_image_map", recref_id, "manif_image_map")

    def delete_person_comment_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_person_comment_map", recref_id, "person_comment_map")

    def delete_person_resource_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_person_resource_map", recref_id, "person_resource_map")

    def delete_person_location_map(self, recref_id: int):
        self._delete_map_by_recref_id("cofk_person_location_map", recref_id, "person_location_map")

    def _delete_map_by_recref_id(self, table: str, recref_id: int, audit_name: str):
        self.check_database_connection()
        command = f"DELETE FROM {table} WHERE recref_id=%s"
        command = self.cursor.mogrify(command, (recref_id,))
        self._print_command(f"DELETE {audit_name}", command)
        self._audit_delete(audit_name)
        self.cursor.execute(command)

    # ==================== CREATE Methods ====================

    def create_resource(self, name: str, url: str, description: str = ""):
        self.check_database_connection()

        command = """INSERT INTO cofk_union_resource
            (resource_name, resource_url, resource_details, creation_user, change_user)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING resource_id"""

        command = self.cursor.mogrify(command, (name, url, description, self.user, self.user))

        self._print_command("INSERT resource", command)
        self._audit_insert("resource")

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    def create_comment(self, comment: str):
        self.check_database_connection()

        command = """INSERT INTO cofk_union_comment
            (comment, creation_user, change_user)
            VALUES (%s, %s, %s)
            RETURNING comment_id"""

        command = self.cursor.mogrify(command, (comment, self.user, self.user))

        self._print_command("INSERT comment", command)
        self._audit_insert("comment")

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    def create_image(self, filename: str, display_order: int, image_credits: str,
                     can_be_displayed: str = 'Y', thumbnail: str = None,
                     licence_details: str = '', licence_url: str = ''):
        self.check_database_connection()

        command = """INSERT INTO cofk_union_image
            (image_filename, display_order, credits, can_be_displayed, thumbnail,
             licence_details, licence_url, creation_user, change_user)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING image_id"""

        command = self.cursor.mogrify(command, (
            filename, display_order, image_credits, can_be_displayed, thumbnail,
            licence_details, licence_url, self.user, self.user
        ))

        self._print_command("INSERT image", command)
        self._audit_insert("image")

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

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
    ):
        self.check_database_connection()

        command = """INSERT INTO cofk_union_manifestation (
            manifestation_id, manifestation_type, work_id,
            id_number_or_shelfmark, printed_edition_details,
            paper_size, paper_type_or_watermark,
            number_of_pages_of_document, number_of_pages_of_text,
            seal, postage_marks, endorsements, non_letter_enclosures,
            manifestation_creation_calendar, manifestation_creation_date,
            manifestation_creation_date_gregorian,
            manifestation_creation_date_year, manifestation_creation_date_month,
            manifestation_creation_date_day,
            manifestation_creation_date2_year, manifestation_creation_date2_month,
            manifestation_creation_date2_day, manifestation_creation_date_is_range,
            manifestation_creation_date_inferred, manifestation_creation_date_uncertain,
            manifestation_creation_date_approx, manifestation_creation_date_as_marked,
            manifestation_is_translation, language_of_manifestation,
            address, manifestation_incipit, manifestation_excipit, manifestation_ps,
            opened, routing_mark_stamp, routing_mark_ms, handling_instructions,
            stored_folded, postage_costs_as_marked, postage_costs,
            non_delivery_reason, date_of_receipt_as_marked,
            manifestation_receipt_calendar, manifestation_receipt_date,
            manifestation_receipt_date_gregorian,
            manifestation_receipt_date_year, manifestation_receipt_date_month,
            manifestation_receipt_date_day,
            manifestation_receipt_date2_year, manifestation_receipt_date2_month,
            manifestation_receipt_date2_day, manifestation_receipt_date_is_range,
            manifestation_receipt_date_inferred, manifestation_receipt_date_uncertain,
            manifestation_receipt_date_approx, accompaniments,
            creation_user, change_user
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        ) RETURNING manifestation_id"""

        command = self.cursor.mogrify(command, (
            manifestation_id, manifestation_type, work_id,
            id_number_or_shelfmark, printed_edition_details,
            paper_size, paper_type_or_watermark,
            number_of_pages_of_document, number_of_pages_of_text,
            seal, postage_marks, endorsements, non_letter_enclosures,
            manifestation_creation_calendar, manifestation_creation_date,
            manifestation_creation_date_gregorian,
            manifestation_creation_date_year, manifestation_creation_date_month,
            manifestation_creation_date_day,
            manifestation_creation_date2_year, manifestation_creation_date2_month,
            manifestation_creation_date2_day, manifestation_creation_date_is_range,
            manifestation_creation_date_inferred, manifestation_creation_date_uncertain,
            manifestation_creation_date_approx, manifestation_creation_date_as_marked,
            manifestation_is_translation, language_of_manifestation,
            address, manifestation_incipit, manifestation_excipit, manifestation_ps,
            opened, routing_mark_stamp, routing_mark_ms, handling_instructions,
            stored_folded, postage_costs_as_marked, postage_costs,
            non_delivery_reason, date_of_receipt_as_marked,
            manifestation_receipt_calendar, manifestation_receipt_date,
            manifestation_receipt_date_gregorian,
            manifestation_receipt_date_year, manifestation_receipt_date_month,
            manifestation_receipt_date_day,
            manifestation_receipt_date2_year, manifestation_receipt_date2_month,
            manifestation_receipt_date2_day, manifestation_receipt_date_is_range,
            manifestation_receipt_date_inferred, manifestation_receipt_date_uncertain,
            manifestation_receipt_date_approx, accompaniments,
            self.user, self.user
        ))

        self._print_command("INSERT manifestation", command)
        self._audit_insert("manifestation")

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    # ==================== CREATE Mapping Table Entries ====================

    def _create_map_entry(self, table: str, fields: List[str], values: List,
                          relationship_type: str, audit_name: str) -> int:
        """Generic method to create mapping table entries."""
        self.check_database_connection()

        all_fields = fields + ['relationship_type', 'creation_user', 'change_user']
        all_values = list(values) + [relationship_type, self.user, self.user]

        placeholders = ', '.join(['%s'] * len(all_values))
        field_names = ', '.join(all_fields)

        command = f"""INSERT INTO {table} ({field_names})
            VALUES ({placeholders})
            RETURNING recref_id"""

        command = self.cursor.mogrify(command, all_values)

        self._print_command(f"INSERT {audit_name}", command)
        self._audit_insert(audit_name)

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    # Work-Person relationships
    def create_work_person_map(self, work_id: str, person_id: str,
                                relationship_type: str) -> int:
        return self._create_map_entry(
            "cofk_work_person_map",
            ["work_id", "person_id"],
            [work_id, person_id],
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
            ["work_id", "location_id"],
            [work_id, location_id],
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
            ["work_id", "comment_id"],
            [work_id, comment_id],
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
            ["work_id", "resource_id"],
            [work_id, resource_id],
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
            ["work_from_id", "work_to_id"],
            [work_from_id, work_to_id],
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
            ["person_id", "comment_id"],
            [person_id, comment_id],
            relationship_type,
            "person_comment_map"
        )

    def create_relationship_note_on_person(self, comment_id: int, person_id: str) -> int:
        return self.create_person_comment_map(person_id, comment_id, REL_TYPE_COMMENT_REFERS_TO)

    # Person-Resource relationships
    def create_person_resource_map(self, person_id: str, resource_id: int) -> int:
        return self._create_map_entry(
            "cofk_person_resource_map",
            ["person_id", "resource_id"],
            [person_id, resource_id],
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
            ["person_id", "location_id"],
            [person_id, location_id],
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
            ["manifestation_id", "comment_id"],
            [manifestation_id, comment_id],
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
            ["manif_id", "inst_id"],
            [manifestation_id, institution_id],
            relationship_type,
            "manif_inst_map"
        )

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

        # Get next iwork_id
        self.cursor.execute("SELECT nextval('cofk_union_work_iwork_id_seq'::regclass)")
        iwork_id = self.cursor.fetchone()[0]

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

        command = """INSERT INTO cofk_union_work (
            work_id, iwork_id, description, date_of_work_as_marked, original_calendar,
            date_of_work_std, date_of_work_std_gregorian,
            date_of_work_std_year, date_of_work_std_month, date_of_work_std_day,
            date_of_work2_std_year, date_of_work2_std_month, date_of_work2_std_day,
            date_of_work_std_is_range, date_of_work_inferred, date_of_work_uncertain,
            date_of_work_approx, authors_as_marked, addressees_as_marked,
            authors_inferred, authors_uncertain, addressees_inferred, addressees_uncertain,
            destination_as_marked, origin_as_marked, destination_inferred, destination_uncertain,
            origin_inferred, origin_uncertain, abstract, keywords, work_is_translation,
            incipit, explicit, ps, original_catalogue, accession_code, work_to_be_deleted,
            editors_notes, edit_status, relevant_to_cofk, creation_user, change_user
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )"""

        command = self.cursor.mogrify(command, (
            work_id, iwork_id, description, date_of_work_as_marked, original_calendar,
            date_of_work_std, date_of_work_std_gregorian,
            date_of_work_std_year, date_of_work_std_month, date_of_work_std_day,
            date_of_work2_std_year, date_of_work2_std_month, date_of_work2_std_day,
            date_of_work_std_is_range, date_of_work_inferred, date_of_work_uncertain,
            date_of_work_approx, authors_as_marked, addressees_as_marked,
            authors_inferred, authors_uncertain, addressees_inferred, addressees_uncertain,
            destination_as_marked, origin_as_marked, destination_inferred, destination_uncertain,
            origin_inferred, origin_uncertain, abstract, keywords, work_is_translation,
            incipit, explicit, ps, original_catalogue, accession_code, work_to_be_deleted,
            editors_notes, edit_status, relevant_to_cofk, self.user, self.user
        ))

        self._print_command("CREATE work", command)
        self._audit_insert("work")

        self.cursor.execute(command)
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
        self.cursor.execute("SELECT nextval('cofk_union_person_iperson_id_seq'::regclass)")
        iperson_id = self.cursor.fetchone()[0]
        person_id = f"cofk_union_person-iperson_id:{iperson_id:06d}"

        command = """INSERT INTO cofk_union_person (
            person_id, iperson_id, foaf_name, skos_altlabel, skos_hiddenlabel, person_aliases,
            date_of_birth_year, date_of_birth_month, date_of_birth_day, date_of_birth,
            date_of_birth_inferred, date_of_birth_uncertain, date_of_birth_approx,
            date_of_birth_calendar, date_of_birth_is_range,
            date_of_birth2_year, date_of_birth2_month, date_of_birth2_day,
            date_of_death_year, date_of_death_month, date_of_death_day, date_of_death,
            date_of_death_inferred, date_of_death_uncertain, date_of_death_approx,
            date_of_death_calendar, date_of_death_is_range,
            date_of_death2_year, date_of_death2_month, date_of_death2_day,
            gender, is_organisation, organisation_type,
            flourished_year, flourished_month, flourished_day, flourished,
            flourished2_year, flourished2_month, flourished2_day,
            flourished_is_range, flourished_calendar,
            flourished_inferred, flourished_uncertain, flourished_approx,
            editors_notes, further_reading, creation_user, change_user
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING person_id"""

        command = self.cursor.mogrify(command, (
            person_id, iperson_id, primary_name, synonyms, skos_hiddenlabel, aliases,
            birth_year, birth_month, birth_day, date_of_birth,
            birth_inferred, birth_uncertain, birth_approx,
            birth_calendar, birth_is_range,
            birth2_year, birth2_month, birth2_day,
            death_year, death_month, death_day, date_of_death,
            death_inferred, death_uncertain, death_approx,
            death_calendar, death_is_range,
            death2_year, death2_month, death2_day,
            gender, is_org, org_type,
            flourished_year, flourished_month, flourished_day, flourished,
            flourished2_year, flourished2_month, flourished2_day,
            flourished_is_range, flourished_calendar,
            flourished_inferred, flourished_uncertain, flourished_approx,
            editors_notes, further_reading, self.user, self.user
        ))

        self._print_command("INSERT person", command)
        self._audit_insert("person")

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

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
        self.check_database_connection()

        location_list = []
        for value in [element_1_eg_room, element_2_eg_building, element_3_eg_parish,
                      element_4_eg_city, element_5_eg_county, element_6_eg_country,
                      element_7_eg_empire]:
            if value:
                location_list.append(value)

        location_name = ", ".join(location_list)

        command = """INSERT INTO cofk_union_location (
            location_name, latitude, longitude, location_synonyms,
            element_1_eg_room, element_2_eg_building, element_3_eg_parish,
            element_4_eg_city, element_5_eg_county, element_6_eg_country,
            element_7_eg_empire, editors_notes, creation_user, change_user
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING location_id"""

        command = self.cursor.mogrify(command, (
            location_name, latitude, longitude, location_synonyms,
            element_1_eg_room, element_2_eg_building, element_3_eg_parish,
            element_4_eg_city, element_5_eg_county, element_6_eg_country,
            element_7_eg_empire, editors_notes, self.user, self.user
        ))

        self._print_command("INSERT location", command)
        self._audit_insert("location")

        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    # ==================== Language Utilities ====================

    def get_languages_from_code(self, code: str) -> str:
        """Get language names from ISO 639-3 codes (semicolon-separated)."""
        self.check_database_connection()

        codes = code.split(";")
        placeholders = ', '.join(['%s'] * len(codes))

        command = f"""SELECT language_name FROM iso_639_language_codes
            WHERE code_639_3 IN ({placeholders})"""

        command = self.cursor.mogrify(command, codes)
        self.cursor.execute(command)

        languages = [row['language_name'] for row in self.cursor]
        return ", ".join(languages)

    def add_language_to_work(self, work_id: str, language_code: str, notes: str = None):
        """Add a language to a work via cofk_union_language_of_work."""
        self.check_database_connection()

        command = """INSERT INTO cofk_union_language_of_work (work_id, language_code, notes)
            VALUES (%s, %s, %s)
            ON CONFLICT (work_id, language_code) DO NOTHING"""

        command = self.cursor.mogrify(command, (work_id, language_code, notes))
        self._print_command("INSERT language_of_work", command)
        self.cursor.execute(command)
        self._audit_insert("language_of_work")

    def add_language_to_manifestation(self, manifestation_id: str, language_code: str,
                                       notes: str = None):
        """Add a language to a manifestation via cofk_union_language_of_manifestation."""
        self.check_database_connection()

        command = """INSERT INTO cofk_union_language_of_manifestation
            (manifestation_id, language_code, notes)
            VALUES (%s, %s, %s)
            ON CONFLICT (manifestation_id, language_code) DO NOTHING"""

        command = self.cursor.mogrify(command, (manifestation_id, language_code, notes))
        self._print_command("INSERT language_of_manifestation", command)
        self.cursor.execute(command)
        self._audit_insert("language_of_manifestation")

    # ==================== Utility Methods ====================

    @staticmethod
    def get_int_value(value, default: int = None) -> Optional[int]:
        if value is not None and value != '':
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
            raise psycopg2.DatabaseError("Database not connected")

    def database_ok(self) -> bool:
        return bool(self.connection and self.cursor)

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

    def _print_command(self, name: str, command):
        if self.debug:
            print(f" * {name}:", command)

    # ==================== Trigger Methods ====================

    def triggers_enable(self, table_name: str, triggers: List[str] = None):
        triggers = triggers or []
        if not triggers:
            return

        command = f"ALTER TABLE {table_name} "
        command += ", ".join(f"ENABLE TRIGGER {trigger}" for trigger in triggers)
        command += ";"

        self._print_command("ENABLE Triggers", command)
        self.cursor.execute(command)

    def triggers_disable(self, table_name: str, triggers: List[str] = None):
        triggers = triggers or []
        if not triggers:
            return

        command = f"ALTER TABLE {table_name} "
        command += ", ".join(f"DISABLE TRIGGER {trigger}" for trigger in triggers)
        command += ";"

        self._print_command("DISABLE Triggers", command)
        self.cursor.execute(command)
