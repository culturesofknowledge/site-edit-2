import logging
from typing import Iterable, Type

from django import forms
from django.db.models import TextChoices, Choices, Model
from django.forms import CharField
from django.shortcuts import get_object_or_404

from core.forms import get_peron_full_form_url_by_pk
from core.helper import view_utils, data_utils, form_utils
from core.models import Recref
from person.models import CofkUnionPerson
from work.models import CofkCollectWork, CofkUnionWork, CofkWorkPersonMap

log = logging.getLogger(__name__)


class CofkCollectWorkForm(forms.ModelForm):
    class Meta:
        model = CofkCollectWork
        fields = '__all__'
        # exclude = ['_id']


class WorkForm(forms.ModelForm):
    sender_person_id = forms.CharField(required=False)

    authors_as_marked = forms.CharField(required=False)
    authors_inferred = form_utils.ZeroOneCheckboxField(is_str=False)
    authors_uncertain = form_utils.ZeroOneCheckboxField(is_str=False)

    addressees_as_marked = forms.CharField(required=False)
    addressees_inferred = form_utils.ZeroOneCheckboxField(is_str=False)
    addressees_uncertain = form_utils.ZeroOneCheckboxField(is_str=False)

    class Meta:
        model = CofkUnionWork
        fields = (
            'description',
            'authors_as_marked',
            'authors_inferred',
            'authors_uncertain',
            'addressees_as_marked',
            'addressees_inferred',
            'addressees_uncertain',
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
    template_name = 'work/component/author_map_form.html'  # KTODO rename to multi_rel_recref_form.html

    name = forms.CharField(required=False)
    target_id = forms.CharField(required=False, widget=forms.HiddenInput())
    relationship_types = RelationField(UndefinedRelationChoices)

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
                                  records: Iterable[CofkWorkPersonMap], prefix):
        initial_list = []
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
            relationship_type__in=self.fields['relationship_types'].choices_class.values,
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
