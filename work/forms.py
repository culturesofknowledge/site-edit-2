import logging

from django import forms
from django.db.models import TextChoices, Model
from django.forms import CharField

from core import constant
from core.constant import DEFAULT_EMPTY_DATE_STR, REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO
from core.form_label_maps import field_label_map
from core.helper import form_serv, date_serv
from core.helper import widgets_serv
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.form_serv import TargetPersonMRRForm, LocationRecrefField, InstRecrefField, BasicSearchFieldset, \
    SearchCharField, SearchIntField
from core.models import CofkUnionSubject, CofkLookupCatalogue
from institution.models import CofkUnionInstitution
from manifestation.models import CofkUnionManifestation
from work.models import CofkUnionWork
from work.recref_adapter import WorkPersonRecrefAdapter, ManifPersonRecrefAdapter

log = logging.getLogger(__name__)

manif_type_choices = [
    ('ALS', 'Letter'),
    ('D', 'Draft'),
    ('DC', 'Digital copy'),
    ('E', 'Extract'),
    ('O', 'Other'),
    ('P', 'Printed copy'),
    ('S', 'Scribal copy'),
]

manif_letter_opened_choices = [
    ('o', 'Opened'),
    ('p', 'Partially opened'),
    ('u', 'Unopened'),
]


def create_auto_date_field():
    return forms.CharField(required=False,
                           initial=DEFAULT_EMPTY_DATE_STR,
                           empty_value=DEFAULT_EMPTY_DATE_STR,
                           widget=forms.TextInput(dict(readonly='readonly')))


class CorrForm(forms.ModelForm):
    authors_as_marked = forms.CharField(required=False)
    authors_inferred = form_serv.ZeroOneCheckboxField(is_str=False)
    authors_uncertain = form_serv.ZeroOneCheckboxField(is_str=False)

    addressees_as_marked = forms.CharField(required=False)
    addressees_inferred = form_serv.ZeroOneCheckboxField(is_str=False)
    addressees_uncertain = form_serv.ZeroOneCheckboxField(is_str=False)

    # extra field
    selected_author_id = forms.CharField(required=False)
    selected_addressee_id = forms.CharField(required=False)

    class Meta:
        model = CofkUnionWork
        fields = (
            'authors_as_marked',
            'authors_inferred',
            'authors_uncertain',

            'addressees_as_marked',
            'addressees_inferred',
            'addressees_uncertain',
        )


class DatesForm(forms.ModelForm):
    date_of_work_as_marked = forms.CharField(required=False)
    date_of_work_std_is_range = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_work_std_year = form_serv.create_year_field()
    date_of_work_std_month = form_serv.create_month_field()
    date_of_work_std_day = form_serv.create_day_field()
    date_of_work2_std_year = form_serv.create_year_field()
    date_of_work2_std_month = form_serv.create_month_field()
    date_of_work2_std_day = form_serv.create_day_field()
    date_of_work_inferred = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_work_uncertain = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_work_approx = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)

    date_of_work_std = create_auto_date_field()
    date_of_work_std_gregorian = create_auto_date_field()
    original_calendar = CharField(required=False,
                                  widget=forms.RadioSelect(choices=date_serv.calendar_choices))

    class Meta:
        model = CofkUnionWork
        fields = (
            'date_of_work_as_marked',
            'date_of_work_std_is_range',
            'date_of_work_std_year',
            'date_of_work_std_month',
            'date_of_work_std_day',
            'date_of_work2_std_year',
            'date_of_work2_std_month',
            'date_of_work2_std_day',
            'date_of_work_inferred',
            'date_of_work_uncertain',
            'date_of_work_approx',
            'date_of_work_std',
            'date_of_work_std_gregorian',
            'original_calendar',
        )


class PlacesForm(forms.ModelForm):
    origin_as_marked = CharField(required=False)
    origin_inferred = form_serv.ZeroOneCheckboxField(is_str=False)
    origin_uncertain = form_serv.ZeroOneCheckboxField(is_str=False)

    destination_as_marked = CharField(required=False)
    destination_inferred = form_serv.ZeroOneCheckboxField(is_str=False)
    destination_uncertain = form_serv.ZeroOneCheckboxField(is_str=False)

    # extract
    selected_origin_location_id = LocationRecrefField(required=False)
    selected_destination_location_id = LocationRecrefField(required=False)

    class Meta:
        model = CofkUnionWork
        fields = (
            'origin_as_marked',
            'origin_inferred',
            'origin_uncertain',
            'destination_as_marked',
            'destination_inferred',
            'destination_uncertain',
        )


class DetailsForm(forms.ModelForm):
    accession_code = CharField(required=False)
    editors_notes = form_serv.CommonTextareaField()
    incipit = form_serv.CommonTextareaField()
    explicit = form_serv.CommonTextareaField()
    ps = form_serv.CommonTextareaField()
    abstract = form_serv.CommonTextareaField()
    keywords = form_serv.CommonTextareaField()

    class Meta:
        model = CofkUnionWork
        fields = (
            'accession_code',
            'editors_notes',
            'incipit',
            'explicit',
            'ps',
            'abstract',
            'keywords',
        )


class ManifForm(forms.ModelForm):
    manifestation_type = form_serv.CharSelectField(choices=manif_type_choices)

    id_number_or_shelfmark = forms.CharField(required=False)
    printed_edition_details = form_serv.CommonTextareaField()

    manifestation_creation_date_as_marked = forms.CharField(required=False)
    manifestation_creation_date_is_range = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_year = form_serv.create_year_field()
    manifestation_creation_date_month = form_serv.create_month_field()
    manifestation_creation_date_day = form_serv.create_day_field()
    manifestation_creation_date2_year = form_serv.create_year_field()
    manifestation_creation_date2_month = form_serv.create_month_field()
    manifestation_creation_date2_day = form_serv.create_day_field()
    manifestation_creation_date_inferred = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_uncertain = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_approx = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)

    manifestation_creation_date = create_auto_date_field()
    manifestation_creation_date_gregorian = create_auto_date_field()

    manifestation_creation_calendar = CharField(required=False,
                                                widget=forms.RadioSelect(choices=date_serv.calendar_choices))

    date_of_receipt_as_marked = forms.CharField(required=False)
    manifestation_receipt_date_is_range = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_year = form_serv.create_year_field()
    manifestation_receipt_date_month = form_serv.create_month_field()
    manifestation_receipt_date_day = form_serv.create_day_field()
    manifestation_receipt_date2_year = form_serv.create_year_field()
    manifestation_receipt_date2_month = form_serv.create_month_field()
    manifestation_receipt_date2_day = form_serv.create_day_field()
    manifestation_receipt_date_inferred = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_uncertain = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_approx = form_serv.ZeroOneCheckboxField(is_str=False, initial=0)

    manifestation_receipt_date = create_auto_date_field()
    manifestation_receipt_date_gregorian = create_auto_date_field()

    manifestation_receipt_calendar = CharField(required=False,
                                               widget=forms.RadioSelect(choices=date_serv.calendar_choices))

    non_letter_enclosures = form_serv.CommonTextareaField()
    accompaniments = form_serv.CommonTextareaField()

    opened = form_serv.CharSelectField(choices=manif_letter_opened_choices)
    paper_size = forms.CharField(required=False)
    stored_folded = forms.CharField(required=False)
    paper_type_or_watermark = forms.CharField(required=False)
    number_of_pages_of_document = forms.IntegerField(required=False)
    seal = form_serv.CommonTextareaField()
    postage_marks = forms.CharField(required=False)
    postage_costs_as_marked = forms.CharField(required=False)
    postage_costs = forms.CharField(required=False)
    address = form_serv.CommonTextareaField()
    routing_mark_stamp = form_serv.CommonTextareaField()
    routing_mark_ms = form_serv.CommonTextareaField()
    handling_instructions = form_serv.CommonTextareaField()
    endorsements = form_serv.CommonTextareaField()
    non_delivery_reason = forms.CharField(required=False)

    manifestation_is_translation = form_serv.ZeroOneCheckboxField(is_str=False)

    manifestation_incipit = form_serv.CommonTextareaField()
    manifestation_excipit = form_serv.CommonTextareaField()

    # extra fields
    selected_scribe_id = forms.CharField(required=False)
    selected_inst_id = InstRecrefField(required=False)

    class Meta:
        model = CofkUnionManifestation
        fields = (
            'manifestation_type',
            'id_number_or_shelfmark',
            'printed_edition_details',

            'manifestation_creation_date_as_marked',
            'manifestation_creation_date_is_range',
            'manifestation_creation_date_year',
            'manifestation_creation_date_month',
            'manifestation_creation_date_day',
            'manifestation_creation_date2_year',
            'manifestation_creation_date2_month',
            'manifestation_creation_date2_day',
            'manifestation_creation_date_inferred',
            'manifestation_creation_date_uncertain',
            'manifestation_creation_date_approx',
            'manifestation_creation_date',
            'manifestation_creation_date_gregorian',
            'manifestation_creation_calendar',

            'date_of_receipt_as_marked',
            'manifestation_receipt_date_is_range',
            'manifestation_receipt_date_year',
            'manifestation_receipt_date_month',
            'manifestation_receipt_date_day',
            'manifestation_receipt_date2_year',
            'manifestation_receipt_date2_month',
            'manifestation_receipt_date2_day',
            'manifestation_receipt_date_inferred',
            'manifestation_receipt_date_uncertain',
            'manifestation_receipt_date_approx',
            'manifestation_receipt_date',
            'manifestation_receipt_date_gregorian',
            'manifestation_receipt_calendar',

            'non_letter_enclosures',
            'accompaniments',

            'opened',
            'paper_size',
            'stored_folded',
            'paper_type_or_watermark',
            'number_of_pages_of_document',
            'seal',
            'postage_marks',
            'postage_costs_as_marked',
            'postage_costs',
            'address',
            'routing_mark_stamp',
            'routing_mark_ms',
            'handling_instructions',
            'endorsements',
            'non_delivery_reason',

            'manifestation_is_translation',

            'manifestation_incipit',
            'manifestation_excipit',

        )


class CommonWorkForm(forms.Form):
    """ Common fields for work pages """

    catalogue = forms.CharField(required=False, widget=forms.Select())
    catalogue_list = forms.Field(required=False, widget=widgets_serv.Datalist())

    work_to_be_deleted = form_serv.DeleteCheckboxField(is_str=False, initial=0)


class AuthorRelationChoices(TextChoices):
    CREATED = REL_TYPE_CREATED, 'Creator'
    SENT = constant.REL_TYPE_SENT, 'Sender'
    SIGNED = constant.REL_TYPE_SIGNED, 'Signatory'


class AddresseeRelationChoices(TextChoices):
    ADDRESSED_TO = REL_TYPE_WAS_ADDRESSED_TO, 'Recipient'
    INTENDED_FOR = constant.REL_TYPE_INTENDED_FOR, 'Intended recipient'


class ScribeRelationChoices(TextChoices):
    HANDWROTE = 'handwrote', 'Handwrite'
    PARTLY_HANDWROTE = 'partly_handwrote', 'Partly handwrote'


class ManifPersonMRRForm(TargetPersonMRRForm):
    relationship_types = ScribeRelationChoices
    no_date = True

    @classmethod
    def create_recref_adapter(cls, *args, **kwargs) -> RecrefFormAdapter:
        return ManifPersonRecrefAdapter(*args, **kwargs)

    def find_recref_list_by_target_id(self, host_model: Model, target_id):
        return host_model.cofkmanifpersonmap_set.filter(
            person_id=target_id,
            relationship_type__in=self.get_rel_type_choices_values(),
        )


class WorkPersonMRRForm(TargetPersonMRRForm):
    no_date = True

    @classmethod
    def create_recref_adapter(cls, *args, **kwargs) -> RecrefFormAdapter:
        return WorkPersonRecrefAdapter(*args, **kwargs)

    def find_recref_list_by_target_id(self, host_model: Model, target_id):
        return host_model.cofkworkpersonmap_set.filter(
            person_id=target_id,
            relationship_type__in=self.get_rel_type_choices_values(),
        )


class WorkAuthorRecrefForm(WorkPersonMRRForm):
    relationship_types = AuthorRelationChoices


class WorkAddresseeRecrefForm(WorkPersonMRRForm):
    relationship_types = AddresseeRelationChoices


description_help_text = "This is in the style 'DD Mon YYYY: Author/Sender (place) to" \
                        " Addressee (place)', e.g. 8 Mar 1693: Bulkeley, Sir Richard" \
                        " (Dunlaven, County Wicklow) to Lister, Martin (Old Palace Yard, Westminster)."
year_help_text = "Year in which work was created." \
                 " (Use 'is blank' option in Advanced Search to find works without year.)"
month_help_text = "Month (1-12) in which work was created. (Use 'is blank' option to find works without month.)"
day_help_text = "Day on which work was created. (Use 'is blank' option to find works without day.)"
date_of_work_help_text = "To find works from a specified period, enter dates 'from' and 'to' as YYYY or" \
                         " DD/MM/YYYY. Either end of the date-range may be left blank, e.g. <ul><li>From 1633'" \
                         " to find works dated from 1st January 1633 onwards</li><li>'To 1634' to find works dated up" \
                         " to 31st December 1634</li></ul>"
sender_recipient_help_text = "Enter part or all of the name of either the author/sender or the" \
                             " addressee to find all letters either to or from a particular person."
origin_destination_help_text = "The place to or from which a letter was sent, in standard modern format."
places_from_searchable = 'The place from which a letter was sent, in standard modern format.'
places_to_searchable = 'The place to which a letter was sent, in standard modern format.'
flags_help_text = "May contain the words 'Date of work', 'Author/sender', 'Addressee', 'Origin' " \
                  "and/or 'Destination', followed by 'INFERRED', 'UNCERTAIN' or, in the case of date," \
                  " 'APPROXIMATE'. E.g. Author/sender INFERRED."
date_as_marked_help_text = "This field could contain the actual words marked within the " \
                           "letter, such as 'ipsis Kalendis Decembribus C I. I. CCVI', or" \
                           " a modern researcher's notation such as 'n.d.'"
manif_help_text = 'The Manifestations field contains a very brief summary of all the ' \
                  'manifestations of a work. This summary includes document type plus ' \
                  'either repository and shelfmark or printed edition details.</p><p><i>You can ' \
                  'search on both document type and repository at once if you wish, but ' \
                  'please remember, document type comes first in the summary, then ' \
                  'repository, so you need to enter your search terms in that same order. ' \
                  'Also, if entering multiple search terms, you need to separate them ' \
                  'using the wildcard % (percent-sign).</i>'
img_help_text = 'Contains filenames of any scanned images of manifestations.'
abstr_help_text = 'Contains a summary of the contents of the work'
keywords_help_text = 'This field contains keywords, plus a list of places and works mentioned within a work.'
acc_help_text = 'Typically contains the name of the researcher who contributed the data.'
del_help_text = "Yes or No. If 'Yes', the record is marked for deletion."
id_help_text = 'The unique ID for the record within the current CofK database.'
change_help_text = 'Username of the person who last changed the record.'

work_to_be_deleted_choices = [(0, 'No'), (1, 'Yes')]


class CompactSearchFieldset(BasicSearchFieldset):
    title = 'Compact Search'
    template_name = 'work/component/work_compact_search_fieldset.html'

    institution_names = CofkUnionInstitution.objects \
        .order_by('institution_name').values_list('institution_name', flat=True).distinct()
    manif_type = [t[1] for t in manif_type_choices]
    subject_names = CofkUnionSubject.objects.order_by('subject_desc').values_list('subject_desc', flat=True).distinct()
    catalog_names = CofkLookupCatalogue.objects \
        .order_by('catalogue_name').values_list('catalogue_name', flat=True).distinct()

    # Fields shared with both search forms
    description = SearchCharField(help_text=description_help_text)
    description_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    editors_notes = SearchCharField(label=field_label_map['work']['editors_notes'])
    editors_notes_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    sender_or_recipient = SearchCharField(help_text=sender_recipient_help_text)
    sender_or_recipient_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    origin_or_destination = SearchCharField(help_text=origin_destination_help_text)
    origin_or_destination_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    date_of_work_as_marked = SearchCharField(help_text=date_as_marked_help_text)
    date_of_work_as_marked_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    date_of_work_std_year = SearchIntField(min_value=1000, max_value=1850,
                                           label=field_label_map['work']['date_of_work_std_year'],
                                           help_text=year_help_text)
    date_of_work_std_year_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)

    date_of_work_std_month = SearchIntField(min_value=1, max_value=12,
                                            label=field_label_map['work']['date_of_work_std_month'],
                                            help_text=month_help_text)
    date_of_work_std_month_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)

    date_of_work_std_day = SearchIntField(min_value=1, max_value=31,
                                          label=field_label_map['work']['date_of_work_std_day'],
                                          help_text=day_help_text)
    date_of_work_std_day_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)

    date_of_work_std_from = forms.DateField(required=False,
                                            widget=widgets_serv.SearchDateTimeInput(attrs={'class': 'searchfield'}))
    date_of_work_std_to = forms.DateField(required=False,
                                          widget=widgets_serv.SearchDateTimeInput(attrs={'class': 'searchfield'}))
    date_of_work_std_info = date_of_work_help_text

    creators_searchable = SearchCharField(label=field_label_map['work']['creators_searchable'])
    creators_searchable_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    notes_on_authors = SearchCharField(label=field_label_map['work']['notes_on_authors'])
    notes_on_authors_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    addressees_searchable = SearchCharField(label=field_label_map['work']['addressees_searchable'])
    addressees_searchable_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    places_from_searchable = SearchCharField(label=field_label_map['work']['places_from_searchable'],
                                             help_text=places_from_searchable)
    places_from_searchable_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    places_to_searchable = SearchCharField(label=field_label_map['work']['places_to_searchable'],
                                           help_text=places_to_searchable)
    places_to_searchable_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    flags = SearchCharField(help_text=flags_help_text)
    flags_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    images = SearchCharField(help_text=img_help_text)
    images_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    manifestations_searchable = SearchCharField(label=field_label_map['work']['manifestations_searchable'],
                                                help_text=manif_help_text)
    manifestations_searchable_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    related_resources = SearchCharField()
    related_resources_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    language_of_work = SearchCharField()
    language_of_work_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    subjects = SearchCharField()
    subjects_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    abstract = SearchCharField(help_text=abstr_help_text)
    abstract_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    general_notes = SearchCharField()
    general_notes_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    original_catalogue = SearchCharField()
    original_catalogue_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    accession_code = SearchCharField(label=field_label_map['work']['accession_code'], help_text=acc_help_text)
    accession_code_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    work_to_be_deleted = form_serv.ZeroOneCheckboxField(required=False)

    iwork_id = SearchCharField(label=field_label_map['work']['iwork_id'], help_text=id_help_text)
    iwork_id_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)


class ExpandedSearchFieldset(CompactSearchFieldset):
    title = 'Expanded Search'
    template_name = 'work/component/work_expanded_search_fieldset.html'

    origin_as_marked = SearchCharField()
    origin_as_marked_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    destination_as_marked = SearchCharField()
    destination_as_marked_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    mentioned_searchable = SearchCharField(label=field_label_map['work']['mentioned_searchable'],
                                           help_text='This field contains a list of people mentioned within a work.')
    mentioned_searchable_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    keywords = SearchCharField(help_text=keywords_help_text)
    keywords_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)
