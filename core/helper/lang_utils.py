import logging
from typing import Iterable

from django import forms

from core.helper import model_utils, form_utils, widgets_utils
from core.models import CofkUnionFavouriteLanguage

log = logging.getLogger(__name__)

def get_language_choices():
    return list(CofkUnionFavouriteLanguage.objects.
                values_list('language_code__language_name', 'language_code__code_639_3').
                order_by('language_code__language_name'))


class LangModelAdapter:

    def create_instance_by_owner_id(self, owner_id):
        raise NotImplementedError()


def create_lang_formset(lang_models: Iterable, lang_rec_id_name: str,
                        request_data=None, prefix='lang', extra=0):
    initial_list = model_utils.models_to_dict_list(lang_models)
    initial_list = list(initial_list)
    code_name_dict = {code: name for name, code in dict(get_language_choices()).items()}
    for initial in initial_list:
        initial['lang_name'] = code_name_dict.get(initial['language_code_id'],
                                                  'Unknown Language')
        initial['lang_rec_id'] = initial[lang_rec_id_name]

    return form_utils.create_formset(
        LangForm,
        post_data=request_data or None,
        prefix=prefix,
        extra=extra,
        initial_list=initial_list
    )


class LangForm(forms.Form):
    notes = forms.CharField(required=False)
    lang_name = forms.CharField(required=False, widget=forms.HiddenInput())
    is_delete = form_utils.DeleteCheckboxField()
    lang_rec_id = forms.IntegerField(required=False, widget=forms.HiddenInput())


class NewLangForm(forms.Form):
    new_language = forms.CharField(required=False, widget=forms.TextInput({
        'list': 'id_language_list',
    }))

    language_list = forms.Field(required=False, widget=widgets_utils.Datalist(choices=get_language_choices()))

    def remove_selected_lang_choices(self, selected_langs: Iterable):
        choices = self.fields['language_list'].widget.choices
        selected_codes = {l.language_code_id for l in selected_langs}
        new_choices = [c for c in choices if c[1] not in selected_codes]
        new_choices = sorted(new_choices)
        self.fields['language_list'].widget.choices = new_choices


def add_new_lang_record(note_list: Iterable[str], lang_name_list: Iterable[str],
                        owner_id, lang_model_adapter: "LangModelAdapter"):
    lang_code_map = dict(get_language_choices())
    lang_name_list = list(lang_name_list)
    for _name in lang_name_list:
        if _name not in lang_code_map:
            raise ValueError(f'unexpected language name [{_name}]')

    lang_code_list = (lang_code_map[n] for n in lang_name_list)
    for note, code in zip(note_list, lang_code_list):
        lang = lang_model_adapter.create_instance_by_owner_id(owner_id)
        lang.language_code_id = code
        lang.notes = note
        lang.save()


def maintain_lang_records(lang_forms: Iterable[LangForm], find_lang_fn):
    for lang_form in lang_forms:
        lang_rec_id = lang_form.cleaned_data['lang_rec_id']

        if lang_form.cleaned_data['is_delete']:
            # delete record
            log.info('delete language record [{}] '.format(lang_rec_id))
            find_lang_fn(lang_rec_id).delete()
        elif lang_form.has_changed():
            # update record
            notes = lang_form.cleaned_data['notes']
            log.info('update language record [{}][{}] '.format(lang_rec_id, notes))
            lang = find_lang_fn(lang_rec_id)
            lang.notes = notes
            lang.save()
