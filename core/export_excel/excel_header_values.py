from typing import Iterable

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
            '',  # KTODO Author
            '',  # KTODO Author EMLO ID
            obj.authors_as_marked,
            obj.authors_inferred,
            obj.authors_uncertain,
            '',  # KTODO Notes on Author in relation to letter
            '',  # KTODO Recipient
            '',  # KTODO Recipient EMLO ID
            obj.addressees_as_marked,
            obj.addressees_inferred,
            obj.addressees_uncertain,
            '',  # KTODO Notes on Recipient in relation to letter
            '',  # KTODO Origin name
            '',  # KTODO Origin EMLO ID
            obj.origin_as_marked,
            obj.origin_inferred,
            obj.origin_uncertain,
            '',  # KTODO Notes on Origin in relation to letter
            '',  # KTODO Destination name
            '',  # KTODO Destination EMLO ID
            obj.destination_as_marked,
            obj.destination_inferred,
            obj.destination_uncertain,
            '',  # KTODO Notes on Destination in relation to letter
            obj.abstract,
            obj.keywords,
            '',  # KTODO Language(s)
            obj.work.incipit,
            obj.work.explicit,
            '',  # KTODO People mentioned
            '',  # KTODO EMLO IDs of people mentioned
            '',  # KTODO Notes on people mentioned
            '',  # KTODO Original Catalogue name
            obj.accession_code,
            '',  # KTODO Matching letter(s) in alternative EMLO catalogue(s) (self reference also)
            '',  # KTODO Match id number
            '',  # KTODO Related Resource IDs [er = number for link to EMLO letter]
            '',  # KTODO General notes for public display
            obj.work.uuid,
            '',  # KTODO EMLO URL
        )
