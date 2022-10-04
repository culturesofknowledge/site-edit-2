import collections
import logging
from typing import Iterable, Callable

from django import forms
from django.db.models import TextChoices
from django.forms import CharField
from django.shortcuts import get_object_or_404

from core.forms import get_peron_full_form_url_by_pk
from core.helper import view_utils, data_utils
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

    class Meta:
        model = CofkUnionWork
        fields = (
            'description',
        )


class WorkPersonRelationChoices(TextChoices):
    CREATED = 'created', 'Creator'
    SENT = 'sent', 'Sender'
    SIGNED = 'signed', 'Signatory'


class WorkPersonRelationField(CharField):

    def __init__(self, *args, **kwargs):
        widget = forms.CheckboxSelectMultiple(
            choices=WorkPersonRelationChoices.choices
        )
        super().__init__(*args, required=False, widget=widget, **kwargs)

    def prepare_value(self, value):
        """
        value: should be list of relation_types
        """
        value: list[str] = super().prepare_value(value)
        selected_values = set(value)
        possible_values = set(WorkPersonRelationChoices.values)

        unexpected_values = selected_values - possible_values
        if unexpected_values:
            logging.warning(f'unexpected relationship_type [{unexpected_values}] ')

        selected_values = selected_values & possible_values
        return list(selected_values)

    def clean(self, user_input_values):
        return user_input_values  # return as list


class WorkPersonMapForm(forms.Form):
    template_name = 'work/component/work_person_map_form.html'

    name = forms.CharField(required=False)
    target_id = forms.CharField(required=False, widget=forms.HiddenInput())
    relationship_types = WorkPersonRelationField()

    @property
    def target_url(self):
        return get_peron_full_form_url_by_pk(self.initial.get('target_id'))

    def create_or_delete(self, work: CofkUnionWork, username):
        """
        create or delete CofkWorkPersonMap
        """
        if not self.is_valid():
            logging.warning('do nothing is invalid')
            return

        data: dict = self.cleaned_data
        selected_rel_types = set(data['relationship_types'])

        org_maps: list[CofkWorkPersonMap] = list(work.cofkworkpersonmap_set.filter(
            person_id=data['target_id'],
            relationship_type__in=WorkPersonRelationChoices.values,
        ))

        # delete unchecked relation
        _maps = (m for m in org_maps if m.relationship_type not in selected_rel_types)
        for m in _maps:
            log.info(f'delete [{m.relationship_type}][{m}]')
            m.delete()

        # add checked relation
        new_types = selected_rel_types - {m.relationship_type for m in org_maps}
        person = get_object_or_404(CofkUnionPerson, pk=data['target_id'])
        for new_type in new_types:
            work_person_map = CofkWorkPersonMap()
            work_person_map.person = person
            work_person_map.work = work
            work_person_map.relationship_type = new_type
            work_person_map.update_current_user_timestamp(username)
            work_person_map.save()
            log.info(f'add new [{person.iperson_id}][{work_person_map}]')

    @classmethod
    def create_formset_by_records(cls, post_data, records: Iterable[CofkWorkPersonMap]):
        initial_list = []
        for person_id, work_person_list in data_utils.group_by(records, lambda r: r.person.person_id).items():
            work_person_list: list[CofkWorkPersonMap]
            person = work_person_list[0].person
            initial_list.append({
                'name': person.foaf_name,
                'target_id': person.person_id,
                'relationship_types': {m.relationship_type for m in work_person_list},
            })

        formset = view_utils.create_formset(
            WorkPersonMapForm, post_data=post_data, prefix='work_person',
            initial_list=initial_list,
            extra=0,
        )
        return formset
