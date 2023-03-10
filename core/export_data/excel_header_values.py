from typing import Iterable

from django.urls import reverse

from core import constant
from core.export_data import cell_values
from core.helper import general_model_utils
from core.helper.view_components import HeaderValues
from core.models import CofkUnionResource
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person import person_utils
from person.models import CofkUnionPerson
from work.models import CofkUnionQueryableWork


class ResourceExcelHeaderValues(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            "Resource ID",
            "Resource Name",
            "Resource Details",
            "Resource URL",
            "UUID",
        ]

    def obj_to_values(self, obj: CofkUnionResource) -> Iterable:
        return [
            obj.resource_id,
            obj.resource_name,
            obj.resource_details,
            obj.resource_url,
            obj.uuid,
        ]


class InstExcelHeaderValues(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            "Repository ID",
            "Repository Name",
            "Repository City",
            "Repository Country",
            "Repository Full Address",
            "Repository Latitude",
            "Repository Longitude",
            "Related Resource IDs",
            "UUID",
            "EMLO URL",
            "Create date in database",
            "Last update in database",
        ]

    def obj_to_values(self, obj: CofkUnionInstitution) -> Iterable:
        return [
            obj.institution_id,
            obj.institution_name,
            obj.institution_city,
            obj.institution_country,
            obj.address,
            obj.latitude,
            obj.longitude,
            cell_values.resources_id(obj.resources.all()),
            obj.uuid,
            cell_values.editor_url(reverse('institution:full_form', args=[obj.institution_id])),
            cell_values.simple_datetime(obj.creation_timestamp),
            cell_values.simple_datetime(obj.change_timestamp),
        ]


class ManifExcelHeaderValues(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            "Work (Letter) ID",
            "Manifestation [Letter] ID",
            "Manifestation type",
            "Repository name",
            "Repository ID",
            "Shelfmark and pagination",
            "Printed copy details",
            "Notes on manifestation",
            "UUID",
        ]

    def obj_to_values(self, obj: CofkUnionManifestation) -> Iterable:
        inst = obj.inst
        return [
            obj.work.iwork_id,
            obj.manifestation_id,
            obj.manifestation_type,
            inst and inst.institution_name,
            inst and inst.institution_id,
            obj.id_number_or_shelfmark,
            obj.printed_edition_details,
            cell_values.notes(obj.comments.all()),
            obj.uuid,
        ]


class LocationExcelHeaderValues(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            "Place ID",
            "Place name",
            "Room",
            "Building",
            "Street or parish",
            "Primary place name (city, town, village)",
            "County, State, or Province",
            "Country",
            "Empire",
            "Place name synonyms",
            "Coordinates: Latitude",
            "Coordinates: Longitude",
            "Related Resource IDs",
            "General notes on place",
            "Editors' working notes",
            "UUID",
            "EMLO URL",
        ]

    def obj_to_values(self, obj: CofkUnionLocation) -> Iterable:
        return [
            obj.location_id,
            general_model_utils.get_display_name(obj),
            obj.element_1_eg_room,
            obj.element_2_eg_building,
            obj.element_3_eg_parish,
            obj.element_4_eg_city,
            obj.element_5_eg_county,
            obj.element_6_eg_country,
            obj.element_7_eg_empire,
            obj.location_synonyms,
            obj.latitude,
            obj.longitude,
            cell_values.resources_id(obj.cofklocationresourcemap_set.all()),
            cell_values.notes(obj.comments.all()),
            obj.editors_notes,
            obj.uuid,
            cell_values.editor_url(reverse('location:full_form', args=[obj.location_id])),
        ]


class PersonExcelHeaderValues(HeaderValues):

    def get_header_list(self) -> list[str]:
        return [
            "EMLO Person ID",
            "Person primary name in EMLO",
            "Synonyms",
            "Roles/Titles",
            "Gender",
            "Is Organization (Y=yes;black=no)",
            "Birth year",
            "Death year",
            "Fl. year 1",
            "Fl. year 2",
            "Fl. year is range (0=No; 1=Yes)",
            "General notes on person",
            "Editors' working notes",
            "Related Resource IDs",
            "UUID",
            "EMLO URL",
        ]

    def obj_to_values(self, obj: CofkUnionPerson) -> Iterable:
        return [
            person_utils.get_display_id(obj),
            obj.foaf_name,
            obj.skos_altlabel,
            cell_values.person_roles(obj),
            obj.gender,
            obj.is_organisation,
            obj.date_of_birth_year,
            obj.date_of_death_year,
            obj.flourished_year,
            obj.flourished2_year,
            obj.flourished_is_range,
            cell_values.notes(obj.comments.all()),
            obj.editors_notes,
            cell_values.resources_id(obj.cofkpersonresourcemap_set.all()),
            obj.uuid,
            cell_values.editor_url(reverse('person:full_form', args=[obj.iperson_id])),
        ]


class WorkExcelHeaderValues(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            "EMLO Letter ID Number",
            "Year date",
            "Month date",
            "Day date",
            "Standard gregorian date",
            "Date is range (0=No; 1=Yes)",
            "Year 2nd date (range)",
            "Month 2nd date (range)",
            "Day 2nd date (range)",
            "Calendar of date provided to EMLO (G=Gregorian; JJ=Julian, year start 1 January; JM=Julian, year start March, U=Unknown)",
            "Date as marked on letter",
            "Date uncertain (0=No; 1=Yes)",
            "Date approximate (0=No; 1=Yes)",
            "Date inferred (0=No; 1=Yes)",
            "Notes on date",
            "Author",
            "Author EMLO ID",
            "Author as marked in body/text of letter",
            "Author inferred (0=No; 1=Yes)",
            "Author uncertain (0=No; 1=Yes)",
            "Notes on Author in relation to letter",
            "Recipient",
            "Recipient EMLO ID",
            "Recipient as marked in body/text of letter",
            "Recipient inferred (0=No; 1=Yes)",
            "Recipient uncertain (0=No; 1=Yes)",
            "Notes on Recipient in relation to letter",
            "Origin name",
            "Origin EMLO ID",
            "Origin as marked in body/text of letter",
            "Origin inferred (0=No; 1=Yes)",
            "Origin uncertain (0=No; 1=Yes)",
            "Notes on Origin in relation to letter",
            "Destination name",
            "Destination EMLO ID",
            "Destination as marked in body/text of letter",
            "Destination inferred (0=No; 1=Yes)",
            "Destination uncertain (0=No; 1=Yes)",
            "Notes on Destination in relation to letter",
            "Abstract",
            "Keywords",
            "Language(s)",
            "Incipit",
            "Explicit",
            "People mentioned",
            "EMLO IDs of people mentioned",
            "Notes on people mentioned",
            "Original Catalogue name",
            "Source",
            "Matching letter(s) in alternative EMLO catalogue(s) (self reference also)",
            "Match id number",
            "Related Resource IDs [er = number for link to EMLO letter]",
            "General notes for public display",
            "Editors' working notes",
            "UUID",
            "EMLO URL",
        ]

    def obj_to_values(self, obj: CofkUnionQueryableWork) -> Iterable:
        author_name, author_id = cell_values.name_id(
            obj.work.find_persons_by_rel_type([
                constant.REL_TYPE_CREATED,
                constant.REL_TYPE_SENT,
                constant.REL_TYPE_SIGNED,
            ]))
        recipient_name, recipient_id = cell_values.name_id(
            obj.work.find_persons_by_rel_type([
                constant.REL_TYPE_WAS_ADDRESSED_TO,
                constant.REL_TYPE_INTENDED_FOR,
            ]))

        origin_name, origin_id = cell_values.name_id(
            obj.work.find_locations_by_rel_type(constant.REL_TYPE_WAS_SENT_FROM))
        dest_name, dest_id = cell_values.name_id(
            obj.work.find_locations_by_rel_type(constant.REL_TYPE_WAS_SENT_TO))

        person_mentioned_name, person_mentioned_id = cell_values.name_id(
            obj.work.find_persons_by_rel_type(constant.REL_TYPE_PEOPLE_MENTIONED_IN_WORK))

        match_work_name, match_work_id = cell_values.name_id(
            obj.work.find_work_to_list_by_rel_type(constant.REL_TYPE_WORK_MATCHES))

        return (
            obj.iwork_id,
            obj.work.date_of_work_std_year,
            obj.work.date_of_work_std_month,
            obj.work.date_of_work_std_day,
            obj.work.date_of_work_std_gregorian,
            obj.work.date_of_work_std_is_range,
            obj.work.date_of_work2_std_year,
            obj.work.date_of_work2_std_month,
            obj.work.date_of_work2_std_day,
            obj.work.original_calendar,
            obj.date_of_work_as_marked,
            obj.date_of_work_uncertain,
            obj.date_of_work_approx,
            obj.date_of_work_inferred,
            cell_values.notes(obj.work.date_comments),
            author_name,
            author_id,
            obj.authors_as_marked,
            obj.authors_inferred,
            obj.authors_uncertain,
            cell_values.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_AUTHOR)),
            recipient_name,
            recipient_id,
            obj.addressees_as_marked,
            obj.addressees_inferred,
            obj.addressees_uncertain,
            cell_values.notes(obj.work.addressee_comments),
            origin_name,
            origin_id,
            obj.origin_as_marked,
            obj.origin_inferred,
            obj.origin_uncertain,
            cell_values.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_ORIGIN)),
            dest_name,
            dest_id,
            obj.destination_as_marked,
            obj.destination_inferred,
            obj.destination_uncertain,
            cell_values.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_DESTINATION)),
            obj.abstract,
            obj.keywords,
            obj.language_of_work,
            obj.work.incipit,
            obj.work.explicit,
            person_mentioned_name,
            person_mentioned_id,
            cell_values.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_PEOPLE_MENTIONED_IN_WORK)),
            obj.original_catalogue,
            obj.accession_code,
            match_work_name,
            match_work_id,
            cell_values.resources_id(obj.work.cofkworkresourcemap_set.all()),
            cell_values.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_REFERS_TO)),
            obj.editors_notes,
            obj.work.uuid,
            cell_values.editor_url(reverse('work:corr_form', args=[obj.iwork_id])),
        )
