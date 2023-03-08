from typing import Iterable

from django.conf import settings
from django.urls import reverse

from core import constant
from core.export_excel import export_excel_utils
from core.helper.view_components import HeaderValues
from work.models import CofkUnionQueryableWork


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
        author_name, author_id = export_excel_utils.name_id(
            obj.work.find_persons_by_rel_type([
                constant.REL_TYPE_CREATED,
                constant.REL_TYPE_SENT,
                constant.REL_TYPE_SIGNED,
            ]))
        recipient_name, recipient_id = export_excel_utils.name_id(
            obj.work.find_persons_by_rel_type([
                constant.REL_TYPE_WAS_ADDRESSED_TO,
                constant.REL_TYPE_INTENDED_FOR,
            ]))

        origin_name, origin_id = export_excel_utils.name_id(
            obj.work.find_locations_by_rel_type(constant.REL_TYPE_WAS_SENT_FROM))
        dest_name, dest_id = export_excel_utils.name_id(
            obj.work.find_locations_by_rel_type(constant.REL_TYPE_WAS_SENT_TO))

        person_mentioned_name, person_mentioned_id = export_excel_utils.name_id(
            obj.work.find_persons_by_rel_type(constant.REL_TYPE_PEOPLE_MENTIONED_IN_WORK))

        match_work_name, match_work_id = export_excel_utils.name_id(
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
            export_excel_utils.notes(obj.work.date_comments),
            author_name,
            author_id,
            obj.authors_as_marked,
            obj.authors_inferred,
            obj.authors_uncertain,
            export_excel_utils.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_AUTHOR)),
            recipient_name,
            recipient_id,
            obj.addressees_as_marked,
            obj.addressees_inferred,
            obj.addressees_uncertain,
            export_excel_utils.notes(obj.work.addressee_comments),
            origin_name,
            origin_id,
            obj.origin_as_marked,
            obj.origin_inferred,
            obj.origin_uncertain,
            export_excel_utils.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_ORIGIN)),
            dest_name,
            dest_id,
            obj.destination_as_marked,
            obj.destination_inferred,
            obj.destination_uncertain,
            export_excel_utils.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_DESTINATION)),
            obj.abstract,
            obj.keywords,
            obj.language_of_work,
            obj.work.incipit,
            obj.work.explicit,
            person_mentioned_name,
            person_mentioned_id,
            export_excel_utils.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_PEOPLE_MENTIONED_IN_WORK)),
            obj.original_catalogue,
            obj.accession_code,
            match_work_name,
            match_work_id,
            export_excel_utils.common_join_text((r.resource_id for r in obj.work.cofkworkresourcemap_set.all())),
            export_excel_utils.notes(obj.work.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_REFERS_TO)),
            obj.editors_notes,
            obj.work.uuid,
            '{}{}'.format(
                settings.EXPORT_ROOT_URL,
                reverse('work:corr_form', args=[obj.iwork_id])
            ),
        )
