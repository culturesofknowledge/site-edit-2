import logging
from typing import Type

from django import forms
from django.db.models import TextChoices, Model
from django.forms import CharField

from core import constant
from core.constant import DEFAULT_EMPTY_DATE_STR, REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO
from core.helper import form_utils
from core.helper.common_recref_adapter import RecrefFormAdapter, TargetPersonRecrefAdapter
from core.helper.form_utils import SelectedRecrefField, RelationField, TargetPersonMRRForm
from core.models import Recref
from manifestation.models import CofkUnionManifestation, CofkManifPersonMap
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

manif_letter_opened_choices = [
    ('o', 'Opened'),
    ('p', 'Partially opened'),
    ('u', 'Unopened'),
]


class CofkCollectWorkForm(forms.ModelForm):
    class Meta:
        model = CofkCollectWork
        fields = '__all__'
        # exclude = ['_id']


def create_auto_date_field():
    return forms.CharField(required=False,
                           initial=DEFAULT_EMPTY_DATE_STR,
                           empty_value=DEFAULT_EMPTY_DATE_STR,
                           widget=forms.TextInput(dict(readonly='readonly')))


class LocationRecrefField(SelectedRecrefField):
    def get_recref_name(self, target_id):
        from work.views import WorkLocRecrefAdapter
        return WorkLocRecrefAdapter().find_target_display_name_by_id(target_id)


class InstRecrefField(SelectedRecrefField):
    def get_recref_name(self, target_id):
        from work.views import ManifInstRecrefAdapter
        return ManifInstRecrefAdapter().find_target_display_name_by_id(target_id)


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
    date_of_work2_std_year = form_utils.create_year_field()
    date_of_work2_std_month = form_utils.create_month_field()
    date_of_work2_std_day = form_utils.create_day_field()
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


class DetailsForm(forms.ModelForm):
    accession_code = CharField(required=False)
    editors_notes = CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    incipit = CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    explicit = CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    ps = CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    abstract = CharField(required=False, widget=forms.Textarea(dict(rows='4')))
    keywords = CharField(required=False, widget=forms.Textarea(dict(rows='3')))

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
    manifestation_type = form_utils.CharSelectField(choices=manif_type_choices)

    id_number_or_shelfmark = forms.CharField(required=False)
    printed_edition_details = forms.CharField(required=False, widget=forms.Textarea())

    manifestation_creation_date_as_marked = forms.CharField(required=False)
    manifestation_creation_date_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_creation_date_year = form_utils.create_year_field()
    manifestation_creation_date_month = form_utils.create_month_field()
    manifestation_creation_date_day = form_utils.create_day_field()
    manifestation_creation_date2_year = form_utils.create_year_field()
    manifestation_creation_date2_month = form_utils.create_month_field()
    manifestation_creation_date2_day = form_utils.create_day_field()
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
    manifestation_receipt_date2_year = form_utils.create_year_field()
    manifestation_receipt_date2_month = form_utils.create_month_field()
    manifestation_receipt_date2_day = form_utils.create_day_field()
    manifestation_receipt_date_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    manifestation_receipt_date_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)

    manifestation_receipt_date = create_auto_date_field()
    manifestation_receipt_date_gregorian = create_auto_date_field()

    manifestation_receipt_calendar = CharField(required=False,
                                               widget=forms.RadioSelect(choices=original_calendar_choices))

    non_letter_enclosures = forms.CharField(required=False, widget=forms.Textarea(dict(rows='5')))
    accompaniments = forms.CharField(required=False, widget=forms.Textarea(dict(rows='5')))

    # lang_note = forms.MultipleChoiceField(required=False)
    # lang_name = forms.MultipleChoiceField(required=False)

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

    opened = form_utils.CharSelectField(choices=manif_letter_opened_choices)
    paper_size = forms.CharField(required=False)
    stored_folded = forms.CharField(required=False)
    paper_type_or_watermark = forms.CharField(required=False)
    number_of_pages_of_document = forms.IntegerField(required=False)
    seal = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    postage_marks = forms.CharField(required=False)
    postage_costs_as_marked = forms.CharField(required=False)
    postage_costs = forms.CharField(required=False)
    address = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    routing_mark_stamp = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    routing_mark_ms = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    handling_instructions = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    endorsements = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    non_delivery_reason = forms.CharField(required=False)

    manifestation_is_translation = form_utils.ZeroOneCheckboxField(is_str=False)

    manifestation_incipit = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))
    manifestation_excipit = forms.CharField(required=False, widget=forms.Textarea(dict(rows='3')))

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


class CatalogueForm(forms.Form):
    catalogue = forms.CharField(required=False, widget=forms.Select())


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


class WorkPersonRecrefAdapter(TargetPersonRecrefAdapter):

    def __init__(self, recref=None):
        self.recref: CofkUnionWork = recref

    def recref_class(self) -> Type[Recref]:
        return CofkWorkPersonMap

    def set_parent_target_instance(self, recref, parent, target):
        recref.work = parent
        recref.person = target

    def find_recref_records(self, rel_type):
        return self.recref.cofkworkpersonmap_set.filter(relationship_type=rel_type).iterator()


class ManifPersonRecrefAdapter(TargetPersonRecrefAdapter):

    def __init__(self, recref=None):
        self.recref: CofkUnionManifestation = recref

    def recref_class(self) -> Type[Recref]:
        return CofkManifPersonMap

    def set_parent_target_instance(self, recref, parent, target):
        recref.manifestation = parent
        recref.person = target

    def find_recref_records(self, rel_type):
        return self.recref.cofkmanifpersonmap_set.filter(relationship_type=rel_type).iterator()


# class ManifPersonRecrefForm(MultiRelRecrefForm):
#     recref_adapter = ManifPersonRecrefAdapter(None)
#
#     @property
#     def target_url(self):
#         return get_peron_full_form_url_by_pk(self.initial.get('target_id'))
#
#     @classmethod
#     def get_target_name(cls, recref: Recref):
#         return person_utils.get_recref_display_name(recref)
#
#     @classmethod
#     def get_target_id(cls, recref: Recref):
#         cls.recref_adapter.target_id_name()
#         pass
#
#     def find_recref_list_by_target_id(self, host_model: Model, target_id):
#         pass
#
#     def find_target_model(self, target_id):
#         pass
#
#     def create_recref(self, host_model, target_model) -> Recref:
#         pass


class WorkAuthorRecrefForm(WorkPersonMRRForm):
    relationship_types = AuthorRelationChoices


class WorkAddresseeRecrefForm(WorkPersonMRRForm):
    relationship_types = AddresseeRelationChoices
