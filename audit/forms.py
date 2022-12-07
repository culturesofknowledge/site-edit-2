from django import forms

from core.helper import form_utils, widgets_utils
from core.helper.form_utils import CharSelectField

"""
desc_left_to_right
desc_right_to_left
explicit
foaf_name
id_number_or_shelfmark
iperson_id
iwork_id
person_id
relationship_code
relationship_valid_from
relationship_valid_till
skos_altlabel
skos_hiddenlabel
work_id
"""

changed_field_choices = [
    (None, ''),
    ('abbrev', 'Abbrev'),
    ('abstract', 'Abstract'),
    ('abbrev', 'Accession Code'),
    ('accompaniments', 'Accompaniments'),
    ('address', 'Address'),
    ('addressees_as_marked', 'Addressees As Marked'),
    ('addressees_inferred', 'Addressees Inferred'),
    ('addressees_uncertain', 'Addressees Uncertain'),
    ('all_works', 'All Works'),
    ('authors_as_marked', 'Authors As Marked'),
    ('authors_inferred', 'Authors Inferred'),
    ('authors_uncertain', 'Authors Uncertain'),
    ('can_be_displayed', 'Can Be Displayed'),
    ('comment', 'Comment'),
    ('comment_id', 'Comment Id'),
    ('credits', 'Credits'),
    ('date_of_birth', 'Date Of Birth'),
    ('date_of_birth2_day', 'Date Of Birth2 Day'),
    ('date_of_birth2_month', 'Date Of Birth2 Month'),
    ('date_of_birth2_year', 'Date Of Birth2 Year'),
    ('date_of_birth_approx', 'Date Of Birth Approx'),
    ('date_of_birth_calendar', 'Date Of Birth Calendar'),
    ('date_of_birth_day', 'Date Of Birth Day'),
    ('date_of_birth_inferred', 'Date Of Birth Inferred'),
    ('date_of_birth_is_range', 'Date Of Birth Is Range'),
    ('date_of_birth_month', 'Date Of Birth Month'),
    ('date_of_birth_uncertain', 'Date Of Birth Uncertain'),
    ('date_of_birth_year', 'Date Of Birth Year'),
    ('date_of_death', 'Date Of Death'),
    ('date_of_death2_day', 'Date Of Death2 Day'),
    ('date_of_death2_month', 'Date Of Death2 Month'),
    ('date_of_death2_year', 'Date Of Death2 Year'),
    ('date_of_death_approx', 'Date Of Death Approx'),
    ('date_of_death_calendar', 'Date Of Death Calendar'),
    ('date_of_death_day', 'Date Of Death Day'),
    ('date_of_death_inferred', 'Date Of Death Inferred'),
    ('date_of_death_is_range', 'Date Of Death Is Range'),
    ('date_of_death_month', 'Date Of Death Month'),
    ('date_of_death_uncertain', 'Date Of Death Uncertain'),
    ('date_of_death_year', 'Date Of Death Year'),
    ('date_of_receipt_as_marked', 'Date Of Receipt As Marked'),
    ('date_of_work_approx', 'Date Of Work Approx'),
    ('date_of_work_as_marked', 'Date Of Work As Marked'),
    # ('', 'Date of Work - Day (beginning of range or single date)'),
    # ('', 'Date of Work - Day (end of range)'),
    ('date_of_work_std', 'Date of Work (for ordering)'),
    ('date_of_work_std_gregorian', 'Date of Work (for ordering, Gregorian)'),
    ('date_of_work_inferred', 'Date Of Work Inferred'),
    ('date_of_work_std_is_range', 'Date of Work Is Range'),
    # ('', 'Date of Work - Month (beginning of range or single date)'),
    # ('', 'Date of Work - Month (end of range)'),
    ('date_of_work_uncertain', 'Date Of Work Uncertain'),
    # ('', 'Date of Work - Year (beginning of range or single date)'),
    # ('', 'Date of Work - Year (end of range)'),
    ('description', 'Description'),
    ('destination_as_marked', 'Destination As Marked'),
    ('destination_inferred', 'Destination Inferred'),
    ('destination_uncertain', 'Destination Uncertain'),
    ('display_order', 'Display Order'),
    ('editors_notes', 'Editors Notes'),
    ('edit_status', 'Edit Status'),
    ('element_1_eg_room', 'Element 1 Eg Room'),
    ('element_2_eg_building', 'Element 2 Eg Building'),
    ('element_3_eg_parish', 'Element 3 Eg Parish'),
    ('element_4_eg_city', 'Element 4 Eg City'),
    ('element_5_eg_county', 'Element 5 Eg County'),
    ('element_6_eg_country', 'Element 6 Eg Country'),
    ('element_7_eg_empire', 'Element 7 Eg Empire'),
    ('endorsements', 'Endorsements'),
    ('explicit', 'Explicit'),
    ('flourished', 'Flourished'),
    ('flourished2_day', 'Flourished2 Day'),
    ('flourished2_month', 'Flourished2 Month'),
    ('flourished2_year', 'Flourished2 Year'),
    ('flourished_approx', 'Flourished Approx'),
    ('flourished_calendar', 'Flourished Calendar'),
    ('flourished_day', 'Flourished Day'),
    ('flourished_inferred', 'Flourished Inferred'),
    ('flourished_is_range', 'Flourished Is Range'),
    ('flourished_is_range', 'Flourished Is Range'),
    ('flourished_month', 'Flourished Month'),
    ('flourished_uncertain', 'Flourished Uncertain'),
    ('flourished_year', 'Flourished Year'),
    ('further_reading', 'Further Reading'),
    ('gender', 'Gender'),
    ('handling_instructions', 'Handling Instructions'),
    ('id_number_or_shelfmark', 'ID number or shelfmark'),
    ('image_filename', 'Image Filename'),
    ('image_id', 'Image Id'),
    ('images', 'Images'),
    ('incipit', 'Incipit'),
    ('institution_city', 'Institution City'),
    ('institution_city_synonyms', 'Institution City Synonyms'),
    ('institution_country', 'Institution Country'),
    ('institution_country_synonyms', 'Institution Country Synonyms'),
    ('institution_id', 'Institution Id'),
    ('institution_name', 'Institution Name'),
    ('institution_synonyms', 'Institution Synonyms'),
    ('is_organisation', 'Is Organisation'),
    ('keywords', 'Keywords'),
    ('language_code', 'Language Code'),
    ('language_of_manifestation', 'Language Of Manifestation'),
    ('language_of_work', 'Language Of Work'),
    ('latitude', 'Latitude'),
    ('licence_details', 'Licence Details'),
    ('licence_url', 'Licence Url'),
    ('location_id', 'Location Id'),
    ('location_name', 'Location Name'),
    ('location_synonyms', 'Location Synonyms'),
    ('longitude', 'Longitude'),
    ('manifestation_creation_calendar', 'Manifestation Creation Calendar'),
    ('manifestation_creation_date', 'Manifestation Creation Date'),
    ('manifestation_creation_date2_day', 'Manifestation Creation Date2 Day'),
    ('manifestation_creation_date2_month', 'Manifestation Creation Date2 Month'),
    ('manifestation_creation_date2_year', 'Manifestation Creation Date2 Year'),
    ('manifestation_creation_date_approx', 'Manifestation Creation Date Approx'),
    ('manifestation_creation_date_as_marked', 'Manifestation Creation Date As Marked'),
    ('manifestation_creation_date_day', 'Manifestation Creation Date Day'),
    ('manifestation_creation_date_gregorian', 'Manifestation Creation Date Gregorian'),
    ('manifestation_creation_date_inferred', 'Manifestation Creation Date Inferred'),
    ('manifestation_creation_date_is_range', 'Manifestation Creation Date Is Range'),
    ('manifestation_creation_date_month', 'Manifestation Creation Date Month'),
    ('manifestation_creation_date_uncertain', 'Manifestation Creation Date Uncertain'),
    ('manifestation_creation_date_year', 'Manifestation Creation Date Year'),
    ('manifestation_excipit', 'Manifestation Excipit'),
    ('manifestation_id', 'Manifestation Id'),
    ('manifestation_incipit', 'Manifestation Incipit'),
    ('manifestation_is_translation', 'Manifestation Is Translation'),
    ('manifestation_ps', 'Manifestation Ps'),
    ('manifestation_receipt_calendar', 'Manifestation Receipt Calendar'),
    ('manifestation_receipt_date', 'Manifestation Receipt Date'),
    ('manifestation_receipt_date2_day', 'Manifestation Receipt Date2 Day'),
    ('manifestation_receipt_date2_month', 'Manifestation Receipt Date2 Month'),
    ('manifestation_receipt_date2_year', 'Manifestation Receipt Date2 Year'),
    ('manifestation_receipt_date_approx', 'Manifestation Receipt Date Approx'),
    ('manifestation_receipt_date_day', 'Manifestation Receipt Date Day'),
    ('manifestation_receipt_date_gregorian', 'Manifestation Receipt Date Gregorian'),
    ('manifestation_receipt_date_inferred', 'Manifestation Receipt Date Inferred'),
    ('manifestation_receipt_date_is_range', 'Manifestation Receipt Date Is Range'),
    ('manifestation_receipt_date_month', 'Manifestation Receipt Date Month'),
    ('manifestation_receipt_date_uncertain', 'Manifestation Receipt Date Uncertain'),
    ('manifestation_receipt_date_year', 'Manifestation Receipt Date Year'),
    ('manifestation_type', 'Manifestation Type'),
    ('mentioned', 'Mentioned'),
    ('nationality_desc', 'Nationality Desc'),
    ('nationality_id', 'Nationality Id'),
    ('non_delivery_reason', 'Non Delivery Reason'),
    ('non_letter_enclosures', 'Non Letter Enclosures'),
    ('notes', 'Notes'),
    ('number_of_pages_of_document', 'Number Of Pages Of Document'),
    ('number_of_pages_of_text', 'Number Of Pages Of Text'),
    ('organisation_type', 'Organisation Type'),
    ('opened', 'Opened'),
    ('organisation_type', 'Organisation Type'),
    ('org_type_desc', 'Org Type Desc'),
    ('org_type_id', 'Org Type Id'),
    ('original_calendar', 'Original Calendar'),
    ('original_calendar', 'Original Catalogue'),
    ('origin_as_marked', 'Origin As Marked'),
    ('origin_inferred', 'Origin Inferred'),
    ('origin_uncertain', 'Origin Uncertain'),
    ('other_details_summary', 'Other Details Summary'),
    ('other_details_summary_searchable', 'Other Details Summary Searchable'),
    # ('', 'Other versions of name'),
    ('paper_size', 'Paper Size'),
    ('paper_type_or_watermark', 'Paper Type Or Watermark'),
    ('person_aliases', 'Person Aliases'),
    ('iperson_id', 'Person ID'),
    ('person_id', 'Person ID (for internal system use)'),
    ('foaf_name', 'Person or organisation name'),
    ('postage_costs', 'Postage Costs'),
    ('postage_costs_as_marked', 'Postage Costs As Marked'),
    ('postage_marks', 'Postage Marks'),
    ('printed_edition_details', 'Printed Edition Details'),
    ('ps', 'Ps'),
    ('publication_details', 'Publication Details'),
    ('publication_id', 'Publication Id'),
    ('recd', 'Recd'),
    ('relevant_to_cofk', 'Relevant To Cofk'),
    ('resource_details', 'Resource Details'),
    ('resource_id', 'Resource Id'),
    ('resource_name', 'Resource Name'),
    ('resource_url', 'Resource Url'),
    ('role_categories', 'Role Categories'),
    ('role_category_desc', 'Role Category Desc'),
    ('role_category_id', 'Role Category Id'),
    ('routing_mark_ms', 'Routing Mark Ms'),
    ('routing_mark_stamp', 'Routing Mark Stamp'),
    ('seal', 'Seal'),
    ('sent', 'Sent'),
    ('speed_entry_text', 'Speed Entry Text'),
    ('speed_entry_text_id', 'Speed Entry Text Id'),
    ('stored_folded', 'Stored Folded'),
    ('subject_desc', 'Subject Desc'),
    ('subject_id', 'Subject Id'),
    # ('', 'Synonyms'),
    ('thumbnail', 'Thumbnail'),
    ('uuid', 'Uuid'),
    ('iwork_id', 'Work ID'),
    ('work_id', 'Work ID (for internal system use)'),
    ('work_is_translation', 'Work Is Translation'),
    ('work_to_be_deleted', 'Work To Be Deleted')
]
changed_field_choices_dict = dict(changed_field_choices)

change_type_choices = [
    (None, ''),
    ('New', 'New'),
    ('Chg', 'Change'),
    ('Del', 'Delete'),
]

table_name_choices = [
    (None, ''),
    ('cofk_union_comment', 'Comment'),
    ('cofk_union_favourite_language', 'Favourite Language'),
    ('cofk_union_image', 'Image'),
    ('cofk_union_institution', 'Institution'),
    ('cofk_union_language_of_manifestation', 'Language Of Manifestation'),
    ('cofk_union_language_of_work', 'Language Of Work'),
    ('cofk_union_location', 'Location'),
    ('cofk_union_manifestation', 'Manifestation'),
    ('cofk_union_nationality', 'Nationality'),
    ('cofk_union_org_type', 'Org Type'),
    ('cofk_union_person', 'Person'),
    ('cofk_union_person_summary', 'Person Summary'),
    ('cofk_union_publication', 'Publication'),
    ('cofk_union_resource', 'Resource'),
    ('cofk_union_role_category', 'Role Category'),
    ('cofk_union_speed_entry_text', 'Speed Entry Text'),
    ('cofk_union_subject', 'Subject'),
    ('cofk_union_work', 'Work'),
]


class AuditSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'audit/component/audit_search_fieldset.html'

    change_datetime_from = forms.CharField(required=False)
    change_datetime_to = forms.CharField(required=False)
    change_datetime_info = form_utils.datetime_search_info

    change_user = forms.CharField(required=False)
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    table_name = CharSelectField(choices=table_name_choices, )

    record_id = forms.CharField(required=False)
    record_id_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    key_value_text = forms.CharField(required=False, label='Record Desc')
    key_value_text_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    changed_field = CharSelectField(choices=changed_field_choices, )

    change_made = forms.CharField(required=False)
    change_made_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_type = CharSelectField(choices=change_type_choices, )

    audit_id = forms.IntegerField(required=False)
    audit_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)
