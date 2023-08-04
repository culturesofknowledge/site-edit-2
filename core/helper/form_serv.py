import logging
import re
from typing import Iterable, Type

from django import forms
from django.db.models import TextChoices, Choices, Model
from django.forms import BoundField, CharField, Form, formset_factory
from django.template.loader import render_to_string

from core.helper import widgets_serv, recref_serv
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.models import Recref
from person import person_serv
from sharedlib import data_utils
from work.recref_adapter import WorkLocRecrefAdapter, ManifInstRecrefAdapter

log = logging.getLogger(__name__)

short_month_choices = [
    (None, ''),
    (1, 'Jan'),
    (2, 'Feb'),
    (3, 'Mar'),
    (4, 'Apr'),
    (5, 'May'),
    (6, 'Jun'),
    (7, 'Jul'),
    (8, 'Aug'),
    (9, 'Sep'),
    (10, 'Oct'),
    (11, 'Nov'),
    (12, 'Dec'),
]

datetime_search_info = "Enter as dd/mm/yyyy hh:mm or dd/mm/yyyy (please note: dd/mm/yyyy counts as the very " \
                       "start of a day)."


def record_tracker_label_fn_factory(subject='Entry'):
    def _fn(_self):
        context = {k: _self.initial.get(k, None) for k in
                   ['creation_timestamp', 'creation_user', 'change_timestamp', 'change_user', ]}

        context = context | {'subject': subject}
        return render_to_string('core/component/record_tracker_label.html', context)

    return _fn


def filter_and_log_field_names(cleaned_data: dict, field_names: Iterable[str]):
    def _filter_with_log_fn(_field_name):
        if _field_name not in cleaned_data:
            msg = f'field[{_field_name}] not found in cleaned_data'
            log.warning(msg)
            return False
        else:
            return True

    return filter(_filter_with_log_fn, field_names)


def _prepare_valid_field_names(cleaned_data, field_names):
    field_names = [field_names] if isinstance(field_names, str) else field_names
    field_names = filter_and_log_field_names(cleaned_data, field_names)
    return field_names


def clean_by_default_value(cleaned_data: dict, field_names: Iterable[str],
                           default_val, is_empty_fn=None, ):
    is_empty_fn = is_empty_fn or (lambda v: v is None)

    # default value
    for field in _prepare_valid_field_names(cleaned_data, field_names):
        if is_empty_fn(cleaned_data[field]):
            cleaned_data[field] = default_val


class ZeroOneCheckboxField(forms.BooleanField):
    def __init__(self, is_str=True, *args, **kwargs):
        default_kwargs = dict(
            widget=widgets_serv.create_common_checkbox(),
            initial='0',
            required=False,
        )
        kwargs = default_kwargs | kwargs
        super().__init__(*args, **kwargs)

        self.is_str = is_str

    def clean(self, value):
        new_value = super().clean(value)
        if self.is_str:
            new_value = '1' if new_value else '0'
        else:
            new_value = 1 if new_value else 0
        return new_value


class DeleteCheckboxField(ZeroOneCheckboxField):
    def __init__(self, is_str=False, required=False, *args, **kwargs):
        super().__init__(is_str, *args, required=required, **kwargs)
        self.widget.attrs.update({'class': 'warn-checked'})


class SearchCharField(forms.CharField):

    def __init__(self, required=False, *args, **kwargs):
        super().__init__(*args, required=required, **kwargs)
        self.widget.attrs.update({'class': 'searchfield'})


class SearchIntField(forms.IntegerField):

    def __init__(self, required=False, *args, **kwargs):
        super().__init__(*args, required=required, **kwargs)
        self.widget.attrs.update({'class': 'searchfield'})


class IntLookupChoices(TextChoices):
    EQUALS = 'equals', 'equals (=)',
    NOT_EQUAL_TO = 'not_equal_to', 'not equal to (!=)',

    LESS_THAN = 'less_than', 'less than (<)'
    GREATER_THAN = 'greater_than', 'greater than (>)'

    IS_BLANK = 'is_blank', 'is blank',
    NOT_BLANK = 'not_blank', 'not blank',


class StrLookupChoices(TextChoices):
    CONTAINS = 'contains', 'contains',
    DOES_NOT_CONTAIN = 'not_contain', 'not contain',

    STARTS_WITH = 'starts_with', 'starts with',
    DOES_NOT_START_WITH = 'not_start_with', 'not start with',
    ENDS_WITH = 'ends_with', 'ends with',
    DOES_NOT_END_WITH = 'not_end_with', 'not end with',

    EQUALS = 'equals', 'equals (=)',
    NOT_EQUAL_TO = 'not_equal_to', 'not equal to (!=)',

    IS_BLANK = 'is_blank', 'is blank',
    NOT_BLANK = 'not_blank', 'not blank',


class EqualSimpleLookupChoices(TextChoices):
    EQUALS = 'equals', 'equals (=)',
    NOT_EQUAL_TO = 'not_equal_to', 'not equal to (!=)',

    IS_BLANK = 'is_blank', 'is blank',
    NOT_BLANK = 'not_blank', 'not blank',


def create_day_field(required=False):
    return forms.IntegerField(required=required, min_value=1, max_value=31,
                              widget=forms.TextInput(
                                  attrs={
                                      'placeholder': 'DD',
                                      'type': 'number',
                                      'min': 1,
                                      'max': 31,
                                      'class': 'ad-day',
                                  }
                              ))


def create_month_field(required=False):
    return forms.IntegerField(required=required,
                              widget=forms.Select(choices=short_month_choices,
                                                  attrs={
                                                      'class': 'ad-month',
                                                  }
                                                  ))


def create_year_field(required=False, _class=''):
    return forms.IntegerField(required=required, min_value=1, max_value=9999,
                              widget=forms.TextInput(
                                  attrs={
                                      'placeholder': 'YYYY',
                                      'type': 'number',
                                      'min': 1,
                                      'max': 9999,
                                      'class': f'ad-year {_class}',
                                  }
                              ))


def create_lookup_field(choices, required=False):
    return forms.CharField(required=required,
                           widget=forms.Select(choices=choices), )


class SelectedRecrefField(forms.CharField):
    def get_recref_name(self, target_id):
        raise NotImplementedError()

    def get_bound_field(self, form, field_name):
        target_id = form.initial.get(field_name)
        return RecrefSelectBound(form, self, field_name, self.get_recref_name(target_id))


class RecrefSelectBound(BoundField):

    def __init__(self, form, field, name, recref_name):
        super().__init__(form, field, name)
        self.recref_name = recref_name


class CharSelectField(forms.CharField):
    def __init__(self, choices, required=False, **kwargs):
        super().__init__(required=required,
                         widget=forms.Select(choices=choices),
                         initial=choices[0][0],  # this can avoid invalid changed_data
                         **kwargs)


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


class UndefinedRelationChoices(TextChoices):
    UNDEFINED = 'undefined', 'Undefined'


class SubRecrefForm(forms.Form):
    rel_type = 'unknown rel_type'
    rel_type_label = 'unknown rel_type_label'
    recref_id = forms.CharField(required=False, widget=forms.HiddenInput())
    from_date = forms.DateField(required=False, widget=widgets_serv.NewDateInput())
    to_date = forms.DateField(required=False, widget=widgets_serv.NewDateInput())
    is_selected = ZeroOneCheckboxField(required=False, is_str=False)


class MultiRelRecrefForm(forms.Form):
    """
    this a class is form for handle multi relationship choices for one target.
    it has multable choices (checkboxes) for relationship_type
    """
    template_name = 'core/component/multi_rel_recref_form.html'
    no_date = True
    relationship_types = UndefinedRelationChoices

    name = forms.CharField(required=False)
    target_id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def _get_initial_recref(_rel_type):
            for _recref in self.initial.get('recref_list', []):
                if _recref.relationship_type == _rel_type:
                    return _recref
            return None

        self.recref_forms = []
        for rel_type, rel_type_label in self.relationship_types.choices:
            initial = {}
            if initial_recref := _get_initial_recref(rel_type):
                initial_recref: Recref
                initial = {
                    'recref_id': initial_recref.recref_id,
                    'from_date': initial_recref.from_date,
                    'to_date': initial_recref.to_date,
                    'is_selected': 1,
                }
            recref_form = SubRecrefForm(initial=initial)
            recref_form.rel_type = rel_type
            recref_form.rel_type_label = rel_type_label
            self.recref_forms.append(recref_form)

        # register subform's fields for this form
        for recref_form in self.recref_forms:
            for new_field_name, field_name in self._yield_subform_field_names(recref_form.rel_type):
                self.fields[new_field_name] = recref_form.base_fields[field_name]
                if field_name in recref_form.initial:
                    self.initial[new_field_name] = recref_form.initial[field_name]

    def clean(self):
        super().clean()
        recref_list = []
        for recref_form in self.recref_forms:
            recref_data = {field_name: self.cleaned_data.get(new_field_name) for new_field_name, field_name in
                           self._yield_subform_field_names(recref_form.rel_type)}
            recref_data['rel_type'] = recref_form.rel_type
            recref_list.append(recref_data)

        self.cleaned_data['recref_list'] = recref_list
        return self.cleaned_data

    def _yield_subform_field_names(self, rel_type):
        for field_name in ['recref_id', 'from_date', 'to_date', 'is_selected', ]:
            yield f'{rel_type}_{field_name}', field_name

    def get_recref_forms(self):
        for recref_form in self.recref_forms:
            fake_form = {field_name: self[new_field_name]
                         for new_field_name, field_name in self._yield_subform_field_names(recref_form.rel_type)}
            fake_form['rel_type_label'] = recref_form.rel_type_label
            yield fake_form

    @classmethod
    def create_recref_adapter(cls, *args, **kwargs) -> RecrefFormAdapter:
        raise NotImplementedError()

    @classmethod
    def get_rel_type_choices_values(cls):
        return cls.relationship_types.values

    @property
    def target_url(self):
        raise NotImplementedError()

    @classmethod
    def get_target_id(cls, recref: Recref):
        recref_adapter = cls.create_recref_adapter()
        return recref_adapter.get_target_id(recref)

    def find_recref_list_by_target_id(self, host_model: Model, target_id):
        raise NotImplementedError()

    def create_or_delete(self, host_model: Model, username):
        """
        create or delete
        """
        if not self.is_valid():
            logging.warning(f'[{self.__class__.__name__}] do nothing is invalid')
            return

        recref_adapter = self.create_recref_adapter(host_model)
        data: dict = self.cleaned_data
        recref_list = data['recref_list']
        target_model = recref_adapter.find_target_instance(data['target_id'])

        # delete unchecked relation
        del_recref_list = (recref for recref in recref_list
                           if recref.get('recref_id') and not recref.get('is_selected'))
        for recref_data in del_recref_list:
            db_recref = recref_adapter.recref_class().objects.filter(recref_id=recref_data['recref_id']).first()
            if db_recref:
                log.info(f'delete [{db_recref.relationship_type}][{db_recref}]')
                db_recref.delete()
            else:
                log.info(f'skip delete recref not found [{recref_data["rel_type"]}][{recref_data["recref_id"]}]')

        # add checked relation
        new_recref_list = (recref for recref in recref_list
                           if not recref.get('recref_id') and recref.get('is_selected'))
        for recref_data in new_recref_list:
            recref = recref_adapter.upsert_recref(recref_data['rel_type'], host_model, target_model, username=username)
            recref = recref_serv.fill_common_recref_field(recref, recref_data, username)
            recref.save()
            log.info(f'add new [{target_model}][{recref}]')

        # update date from to
        if self.no_date:
            update_recref_list = []
        else:
            update_recref_list = (recref for recref in recref_list
                                  if recref.get('recref_id') and recref.get('is_selected'))
        for recref_data in update_recref_list:
            db_recref = recref_adapter.recref_class().objects.filter(recref_id=recref_data['recref_id']).first()
            if db_recref:
                if (db_recref.from_date != recref_data['from_date'] or
                        db_recref.to_date != recref_data['to_date']):
                    log.info(f'update [{db_recref.relationship_type}][{db_recref}]')
                    db_recref.from_date = recref_data['from_date']
                    db_recref.to_date = recref_data['to_date']
                    db_recref.save()
            else:
                log.info(f'skip update recref not found [{recref_data["rel_type"]}][{recref_data["recref_id"]}]')

    @classmethod
    def create_formset_by_records(cls, post_data,
                                  records: Iterable[Recref], prefix):
        initial_list = []
        recref_adapter = cls.create_recref_adapter()
        records = (r for r in records if r.relationship_type in cls.get_rel_type_choices_values())
        for person_id, recref_list in data_utils.group_by(records, lambda r: cls.get_target_id(r)).items():
            recref_list: list[Recref]
            initial_list.append({
                'name': recref_adapter.find_target_display_name_by_id(
                    recref_adapter.get_target_id(recref_list[0])
                ),
                'target_id': person_id,
                'recref_list': recref_list,
            })

        formset = create_formset(
            cls, post_data=post_data, prefix=prefix,
            initial_list=initial_list,
            extra=0,
        )
        return formset


class TargetPersonMRRForm(MultiRelRecrefForm):
    @property
    def target_url(self):
        return person_serv.get_checked_form_url_by_pk(self.initial.get('target_id'))


def save_multi_rel_recref_formset(multi_rel_recref_formset, parent, request):
    _forms = (f for f in multi_rel_recref_formset if f.has_changed())
    for form in _forms:
        form: MultiRelRecrefForm
        form.create_or_delete(parent, request.user.username)


class CommonTextareaField(forms.CharField):
    def __init__(self, *, required=False, n_rows=3,
                 max_length=None, min_length=None, strip=True, empty_value="", **kwargs):
        widget = forms.Textarea(dict(rows=str(n_rows)))
        super().__init__(required=required, widget=widget,
                         max_length=max_length, min_length=min_length, strip=strip,
                         empty_value=empty_value, **kwargs)


class LocationRecrefField(SelectedRecrefField):
    def get_recref_name(self, target_id):
        return WorkLocRecrefAdapter().find_target_display_name_by_id(target_id)


class InstRecrefField(SelectedRecrefField):
    def get_recref_name(self, target_id):
        return ManifInstRecrefAdapter().find_target_display_name_by_id(target_id)


def build_search_components(sort_by_choices: list[tuple[str, str]], entity: str):
    class SearchComponents(Form):
        template_name = 'core/form/search_components.html'
        sort_by = forms.CharField(label='Sort by',
                                  widget=forms.Select(choices=sort_by_choices,
                                                      attrs={'class': 'searchcontrol'}),
                                  required=False, )

        order = forms.CharField(label='Order',
                                widget=forms.RadioSelect(choices=[
                                    ('asc', 'Ascending'),
                                    ('desc', 'Descending')
                                ], attrs={'class': 'searchcontrol'}),
                                required=False)

        num_record = forms.IntegerField(label=f'{entity} per page',
                                        widget=forms.Select(choices=[
                                            (10, 10),
                                            (50, 50),
                                            (100, 100),
                                            (250, 250),
                                            (500, 500)
                                        ], attrs={'class': 'searchcontrol'}),
                                        required=False, )
        page = forms.IntegerField(widget=forms.HiddenInput())

    return SearchComponents


def create_formset(form_class, post_data=None, prefix=None,
                   initial_list: Iterable[dict] = None,
                   extra=1):
    initial_list = initial_list or []
    initial_list = list(initial_list)
    return formset_factory(form_class, extra=extra)(
        post_data or None,
        prefix=prefix,
        initial=initial_list,
    )


class BasicSearchFieldset(forms.Form):
    change_user = SearchCharField(label='Last edited by',
                                  help_text='Username of the person who last changed the record.')
    change_user_lookup = create_lookup_field(StrLookupChoices.choices)

    change_timestamp_from = forms.DateField(required=False,
                                            widget=widgets_serv.SearchDateTimeInput(attrs={'class': 'searchfield'}))
    change_timestamp_to = forms.DateField(required=False,
                                          widget=widgets_serv.SearchDateTimeInput(attrs={'class': 'searchfield'}))
    change_timestamp_info = datetime_search_info


class EmloLineboxField(CommonTextareaField):
    def __init__(self, n_rows=7, **kwargs):
        super().__init__(n_rows=n_rows, **kwargs)
        self.delimiter = kwargs.pop('delimiter', '; ')

    def prepare_value(self, value):
        new_value = re.sub(self.delimiter, '\r\n', value)
        return super().prepare_value(new_value)

    def clean(self, value):
        new_value = re.sub(r'\r?\n', self.delimiter, value)
        return super().clean(new_value)


class YesEmptyCheckboxField(forms.CharField):
    def __init__(self, *args, **kwargs):
        widget = forms.CheckboxInput({'class': 'elcheckbox'},
                                     check_test=lambda v: v == 'Y')
        default_kwargs = dict(
            widget=widget,
            initial='',
            required=False,
        )
        kwargs = default_kwargs | kwargs
        super().__init__(*args, **kwargs)

    def clean(self, value):
        new_value = super().clean(value)
        return 'Y' if new_value == 'True' else ''
