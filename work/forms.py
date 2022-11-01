import logging
from typing import Iterable, Type

from django import forms
from django.db.models import TextChoices, Choices, Model
from django.forms import CharField, Field
from django.shortcuts import get_object_or_404

from core.forms import get_peron_full_form_url_by_pk
from core.helper import view_utils, data_utils, form_utils, widgets_utils
from core.helper.form_utils import SelectedRecrefField
from core.models import Recref
from location import location_utils
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person.models import CofkUnionPerson
from work.models import CofkCollectWork, CofkUnionWork, CofkWorkPersonMap

log = logging.getLogger(__name__)

original_calendar_choices = [
    ('', 'Unknown'),
    ('G', 'Gregorian'),
    ('JM', 'Julian (year starting 25th Mar)'),
    ('JJ', 'Julian (year starting 1st Jan)'),
    ('O', 'Other'),
]
manif_type_choices = [
    ('ALS', 'Letter'),
    ('D', 'Draft'),
    ('DC', 'Digital copy'),
    ('E', 'Extract'),
    ('O', 'Other'),
    ('P', 'Printed copy'),
    ('S', 'Scribal copy'),
]


class CofkCollectWorkForm(forms.ModelForm):
    class Meta:
        model = CofkCollectWork
        fields = '__all__'
        # exclude = ['_id']


def create_auto_date_field():
    return forms.CharField(required=False,
                           empty_value='9999-12-31',
                           widget=forms.TextInput(dict(readonly='readonly')))


class LocationRecrefField(SelectedRecrefField):
    def get_recref_name(self, target_id):
        loc = target_id and CofkUnionLocation.objects.get(location_id=target_id)
        recref_name = location_utils.get_recref_display_name(loc)
        return recref_name


class CorrForm(forms.ModelForm):
    authors_as_marked = forms.CharField(required=False)
    authors_inferred = form_utils.ZeroOneCheckboxField(is_str=False)
    authors_uncertain = form_utils.ZeroOneCheckboxField(is_str=False)

    addressees_as_marked = forms.CharField(required=False)
    addressees_inferred = form_utils.ZeroOneCheckboxField(is_str=False)
    addressees_uncertain = form_utils.ZeroOneCheckboxField(is_str=False)

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
    date_of_work_std_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_work_std_year = form_utils.create_year_field()
    date_of_work_std_month = form_utils.create_month_field()
    date_of_work_std_day = form_utils.create_day_field()
    date_of_work_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_work_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_work_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)

    date_of_work_std = create_auto_date_field()
    date_of_work_std_gregorian = create_auto_date_field()
    original_calendar = CharField(required=False,
                                  widget=forms.RadioSelect(choices=original_calendar_choices))

    class Meta:
        model = CofkUnionWork
        fields = (
            'date_of_work_as_marked',
            'date_of_work_std_is_range',
            'date_of_work_std_year',
            'date_of_work_std_month',
            'date_of_work_std_day',
            'date_of_work_inferred',
            'date_of_work_uncertain',
            'date_of_work_approx',
            'date_of_work_std',
            'date_of_work_std_gregorian',
            'original_calendar',
        )


class PlacesForm(forms.ModelForm):
    origin_as_marked = CharField(required=False)
    origin_inferred = form_utils.ZeroOneCheckboxField(is_str=False)
    origin_uncertain = form_utils.ZeroOneCheckboxField(is_str=False)

    destination_as_marked = CharField(required=False)
    destination_inferred = form_utils.ZeroOneCheckboxField(is_str=False)
    destination_uncertain = form_utils.ZeroOneCheckboxField(is_str=False)

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


class ManifForm(forms.ModelForm):
    manifestation_type = forms.CharField(required=False,
                                         widget=forms.Select(choices=manif_type_choices), )

    # repository  # KTODO

    id_number_or_shelfmark = forms.CharField(required=False)
    printed_edition_details = forms.CharField(required=False, widget=forms.Textarea())

    manifestation_creation_date_as_marked = forms.CharField(required=False)
    manifestation_creation_date_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_year = form_utils.create_year_field()
    manifestation_creation_date_month = form_utils.create_month_field()
    manifestation_creation_date_day = form_utils.create_day_field()
    manifestation_creation_date_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)

    manifestation_creation_date = create_auto_date_field()
    manifestation_creation_date_gregorian = create_auto_date_field()

    manifestation_creation_calendar = CharField(required=False,
                                                widget=forms.RadioSelect(choices=original_calendar_choices))

    date_of_receipt_as_marked = forms.CharField(required=False)
    manifestation_receipt_date_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_year = form_utils.create_year_field()
    manifestation_receipt_date_month = form_utils.create_month_field()
    manifestation_receipt_date_day = form_utils.create_day_field()
    manifestation_receipt_date_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)

    manifestation_receipt_date = create_auto_date_field()
    manifestation_receipt_date_gregorian = create_auto_date_field()

    manifestation_receipt_calendar = CharField(required=False,
                                               widget=forms.RadioSelect(choices=original_calendar_choices))

    # date_of_work_as_marked = forms.CharField(required=False)
    # date_of_work_std_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    # date_of_work_std_year = form_utils.create_year_field()
    # date_of_work_std_month = form_utils.create_month_field()
    # date_of_work_std_day = form_utils.create_day_field()
    # date_of_work_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    # date_of_work_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    # date_of_work_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    #
    # date_of_work_std = create_auto_date_field()
    # date_of_work_std_gregorian = create_auto_date_field()
    # original_calendar = CharField(required=False,
    #                               widget=forms.RadioSelect(choices=original_calendar_choices))

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
            'manifestation_receipt_date_inferred',
            'manifestation_receipt_date_uncertain',
            'manifestation_receipt_date_approx',
            'manifestation_receipt_date',
            'manifestation_receipt_date_gregorian',
            'manifestation_receipt_calendar',

        )


class UndefinedRelationChoices(TextChoices):
    UNDEFINED = 'undefined', 'Undefined'


class AuthorRelationChoices(TextChoices):
    CREATED = 'created', 'Creator'
    SENT = 'sent', 'Sender'
    SIGNED = 'signed', 'Signatory'


class AddresseeRelationChoices(TextChoices):
    ADDRESSED_TO = 'was_addressed_to', 'Recipient'
    INTENDED_FOR = 'intended_for', 'Intended recipient'


class RelationField(CharField):

    def __init__(self, choices_class: Type[Choices], *args, **kwargs):
        self.choices_class = choices_class
        widget = forms.CheckboxSelectMultiple(
            choices=self.choices_class.choices
        )
        super().__init__(*args, required=False, widget=widget, **kwargs)

    def prepare_value(self, value):
        """
        value: should be list of relation_types
        """
        value: list[str] = super().prepare_value(value)
        selected_values = set(value)
        possible_values = set(self.choices_class.values)

        unexpected_values = selected_values - possible_values
        if unexpected_values:
            logging.warning(f'unexpected relationship_type [{unexpected_values}] ')

        selected_values = selected_values & possible_values
        return list(selected_values)

    def clean(self, user_input_values):
        return user_input_values  # return as list


class MultiRelRecrefForm(forms.Form):
    template_name = 'work/component/multi_rel_recref_form.html'  # KTODO rename to multi_rel_recref_form.html

    name = forms.CharField(required=False)
    target_id = forms.CharField(required=False, widget=forms.HiddenInput())
    relationship_types = RelationField(UndefinedRelationChoices)

    @classmethod
    def get_rel_type_choices_values(cls):
        return cls.base_fields['relationship_types'].choices_class.values

    @property
    def target_url(self):
        raise NotImplementedError()

    @classmethod
    def get_target_name(cls, recref: Recref):
        raise NotImplementedError()

    @classmethod
    def get_target_id(cls, recref: Recref):
        raise NotImplementedError()

    def find_recref_list_by_target_id(self, host_model: Model, target_id):
        raise NotImplementedError()

    def find_target_model(self, target_id):
        raise NotImplementedError()

    def create_recref(self, host_model, target_model) -> Recref:
        raise NotImplementedError()

    def create_or_delete(self, host_model: Model, username):
        """
        create or delete
        """
        if not self.is_valid():
            logging.warning(f'[{self.__class__.__name__}] do nothing is invalid')
            return

        data: dict = self.cleaned_data
        selected_rel_types = set(data['relationship_types'])

        org_maps: list[Recref] = list(self.find_recref_list_by_target_id(host_model, data['target_id']))

        # delete unchecked relation
        _maps = (m for m in org_maps if m.relationship_type not in selected_rel_types)
        for m in _maps:
            log.info(f'delete [{m.relationship_type}][{m}]')
            m.delete()

        # add checked relation
        new_types = selected_rel_types - {m.relationship_type for m in org_maps}
        target_model = self.find_target_model(data['target_id'])
        for new_type in new_types:
            work_person_map = self.create_recref(host_model, target_model)
            work_person_map.relationship_type = new_type
            work_person_map.update_current_user_timestamp(username)
            work_person_map.save()
            log.info(f'add new [{target_model}][{work_person_map}]')

    @classmethod
    def create_formset_by_records(cls, post_data,
                                  records: Iterable[Recref], prefix):
        initial_list = []
        records = (r for r in records if r.relationship_type in cls.get_rel_type_choices_values())
        for person_id, recref_list in data_utils.group_by(records, lambda r: cls.get_target_id(r)).items():
            recref_list: list[Recref]
            initial_list.append({
                'name': cls.get_target_name(recref_list[0]),
                'target_id': person_id,
                'relationship_types': {m.relationship_type for m in recref_list},
            })

        formset = view_utils.create_formset(
            cls, post_data=post_data, prefix=prefix,
            initial_list=initial_list,
            extra=0,
        )
        return formset


class WorkPersonRecrefForm(MultiRelRecrefForm):

    def find_recref_list_by_target_id(self, host_model: Model, target_id):
        return host_model.cofkworkpersonmap_set.filter(
            person_id=target_id,
            relationship_type__in=self.get_rel_type_choices_values(),
        )

    @property
    def target_url(self):
        return get_peron_full_form_url_by_pk(self.initial.get('target_id'))

    @classmethod
    def get_target_name(cls, recref):
        return recref.person.foaf_name

    @classmethod
    def get_target_id(cls, recref):
        return recref.person_id

    def find_target_model(self, target_id):
        return get_object_or_404(CofkUnionPerson, pk=target_id)

    def create_recref(self, host_model, target_model) -> Recref:
        work_person_map = CofkWorkPersonMap()
        work_person_map.work = host_model
        work_person_map.person = target_model
        return work_person_map


class WorkAuthorRecrefForm(WorkPersonRecrefForm):
    relationship_types = RelationField(AuthorRelationChoices)


class WorkAddresseeRecrefForm(WorkPersonRecrefForm):
    relationship_types = RelationField(AddresseeRelationChoices)


class CompactSearchFieldset(forms.Form):
    title = 'Compact Search'
    template_name = 'work/component/work_compact_search_fieldset.html'

    description = forms.CharField(required=False)
    description_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    iwork_id = forms.IntegerField(required=False)
    iwork_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    date_of_work_as_marked = forms.CharField(required=False)
    date_of_work_as_marked_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    foaf_name = forms.CharField(required=False)
    foaf_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    year_from = form_utils.create_year_field()
    year_to = form_utils.create_year_field()

    month_from = form_utils.create_month_field()
    month_to = form_utils.create_month_field()

    day_from = form_utils.create_day_field()
    day_to = form_utils.create_day_field()

    gender = forms.CharField(required=False, widget=forms.Select(
        choices=[
            (None, 'All'),
            ('M', 'Male'),
            ('F', 'Female'),
            ('U', 'Unknown or not applicable'),
        ]
    ))

    person_or_group = forms.CharField(required=False, widget=forms.Select(choices=[
        (None, 'All'),
        ('P', 'Person'),
        ('G', 'Group'),
    ]))

    editors_notes = forms.CharField(required=False)
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    further_reading = forms.CharField(required=False)
    further_reading_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_timestamp_from = forms.DateField(required=False, widget=widgets_utils.NewDateInput())
    change_timestamp_to = forms.DateField(required=False, widget=widgets_utils.NewDateInput())

    change_user = forms.CharField(required=False)
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)


class SearchFieldSetField:
    def __init__(self, field: Field, lookup: Field, description: str):
        self.field = field
        self.lookup = lookup
        self.description = description


class ExpandedSearchFieldset(forms.Form):
    title = 'Expanded Search'
    template_name = 'work/component/work_expanded_search_fieldset.html'

    description = forms.CharField(required=False,
                                  help_text="This is in the style 'DD Mon YYYY: Author/Sender (place) to"
                                            " Addressee (place)', e.g. 8 Mar 1693: Bulkeley, Sir Richard"
                                            " (Dunlaven, County Wicklow) to Lister, Martin (Old Palace"
                                            " Yard, Westminster).")
    description_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    editors_notes = forms.CharField(required=False)
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    sender_or_recipient = forms.CharField(required=False,
                                          help_text="Enter part or all of the name of either the author/sender or the"
                                                    " addressee to find all letters either to or from a particular"
                                                    " person.")
    sender_or_recipient_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
    sender_or_recipient_search_fields = 'creators_searchable,addressees_searchable'

    origin_or_destination = forms.CharField(required=False,
                                            help_text="The place to or from which a letter was sent, in standard"
                                                      " modern format.")
    origin_or_destination_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
    origin_or_destination_search_fields = "places_to_searchable,places_from_searchable"

    date_of_work_as_marked = forms.CharField(required=False,
                                             help_text="This field could contain the actual words marked within the "
                                                       "letter, such as 'ipsis Kalendis Decembribus C I. I. CCVI', or"
                                                       " a modern researcher's notation such as 'n.d.'")
    date_of_work_as_marked_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    author = forms.CharField(required=False)
    author_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    date_of_work_std_year = forms.IntegerField(required=False, min_value=1000, max_value=1850,
                                               help_text="Year in which work was created. (Use 'is blank' option in "
                                                         "Advanced Search to find works without year.)")
    date_of_work_std_year_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    date_of_work_std_month = forms.IntegerField(required=False, min_value=1, max_value=12,
                                                help_text="Month (1-12) in which work was created. (Use 'is blank' "
                                                          "option to find works without month.)")
    date_of_work_std_month_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    date_of_work_std_day = forms.IntegerField(required=False, min_value=1, max_value=31,
                                              help_text="Day on which work was created. (Use 'is blank' option to "
                                                        "find works without day.)")
    date_of_work_std_day_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    date_of_work_std_from = forms.CharField(required=False)
    date_of_work_std_to = forms.CharField(required=False)
    date_of_work_std_info = "To find works from a specified period, enter dates 'from' and 'to' as YYYY or" \
                            " DD/MM/YYYY. Either end of the date-range may be left blank, e.g. <ul><li>From 1633'" \
                            " to find works dated from 1st January 1633 onwards</li><li>'To 1634' to find works dated up" \
                            " to 31st December 1634</li></ul>"

    creators_searchable = forms.CharField(required=False)
    creators_searchable_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    notes_on_authors = forms.CharField(required=False)
    notes_on_authors_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    places_from_searchable = forms.CharField(required=False,
                                             help_text='The place from which a letter was sent, in standard '
                                                       'modern format.')
    places_from_searchable_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    origin_as_marked = forms.CharField(required=False)
    origin_as_marked_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    addressee = forms.CharField(required=False)
    addressee_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    places_to_searchable = forms.CharField(required=False,
                                           help_text='The place to which a letter was sent, in standard modern format.')
    places_to_searchable_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    destination_as_marked = forms.CharField(required=False)
    destination_as_marked_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    flags = forms.CharField(required=False,
                            help_text="May contain the words 'Date of work', 'Author/sender', 'Addressee', 'Origin' "
                                      "and/or 'Destination', followed by 'INFERRED', 'UNCERTAIN' or, in the case of "
                                      "date, 'APPROXIMATE'. E.g. Author/sender INFERRED.")
    flags_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    images = forms.CharField(required=False, help_text='Contains filenames of any scanned images of manifestations.')
    images_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    manifestations = forms.CharField(required=False,
                                     help_text='<p>The Manifestations field contains a very brief summary of all the '
                                               'manifestations of a work. This summary includes document type plus '
                                               'either repository and shelfmark or printed edition details.</p><p><i>You can '
                                               'search on both document type and repository at once if you wish, but '
                                               'please remember, document type comes first in the summary, then '
                                               'repository, so you need to enter your search terms in that same order. '
                                               'Also, if entering multiple search terms, you need to separate them '
                                               'using the wildcard % (percent-sign).</i></p>'
                                               '<div>Document type:<select style="width: unset;"><option>Test</option></select></div>'
                                               '<div>Repository:<select style="width: unset;"><option>Test</option></select></div>')
    manifestations_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    related_resources = forms.CharField(required=False)
    related_resources_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    language_of_work = forms.CharField(required=False)
    language_of_work_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    subjects = forms.CharField(required=False)
    subjects_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    abstracts = forms.CharField(required=False,
                                help_text='Contains a summary of the contents of the work')
    abstracts_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    people_mentioned = forms.CharField(required=False,
                                       help_text='This field contains a list of people mentioned within a work.')
    people_mentioned_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    keywords = forms.CharField(required=False,
                               help_text='This field contains keywords, plus a list of places '
                                         'and works mentioned within a work.')
    keywords_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    general_notes = forms.CharField(required=False)
    general_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    original_catalogue = forms.CharField(required=False,
                                         help_text='<select><option>Possible values</option></select>')
    original_catalogue_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    accession_code = forms.CharField(required=False,
                                     help_text='Typically contains the name of the researcher who contributed the data.')
    accession_code_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    # work_to_be_deleted = form_utils.ZeroOneCheckboxField()
    work_to_be_deleted = forms.CharField(required=False,
                                         help_text="Yes or No. If 'Yes', the record is marked for deletion.")
    work_to_be_deleted_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    work_id = forms.CharField(required=False,
                              help_text='The unique ID for the record within the current CofK database.')
    work_id_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    last_edit_from = forms.CharField(required=False)
    last_edit_to = forms.CharField(required=False)
    last_edit_info = "Enter as dd/mm/yyyy hh:mm or dd/mm/yyyy (please note: dd/mm/yyyy counts as the very " \
                     "start of a day)."

    change_user = forms.CharField(required=False,
                                  help_text='Username of the person who last changed the record.')
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
