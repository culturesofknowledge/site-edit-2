import logging
from typing import Iterable, Type

from django import forms
from django.db.models import TextChoices, Choices, Model
from django.forms import CharField
from django.shortcuts import get_object_or_404

from core.forms import get_peron_full_form_url_by_pk
from core.helper import view_utils, data_utils, form_utils
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

    non_letter_enclosures = forms.CharField(required=False, widget=forms.Textarea(dict(rows='5')))
    accompaniments = forms.CharField(required=False, widget=forms.Textarea(dict(rows='5')))

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

    opened = forms.CharField(required=False, widget=forms.Select(choices=manif_letter_opened_choices))
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
