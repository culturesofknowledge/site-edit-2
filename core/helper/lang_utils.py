import logging
from typing import Iterable

from django import forms

from core.helper import view_utils, model_utils, form_utils

log = logging.getLogger(__name__)

language_choices = [
    ('Ancient Greek', 'grc'),
    ('Ancient Hebrew', 'hbo'),
    ('Arabic', 'ara'),
    ('Armenian', 'hye'),
    ('Assyrian Neo-Aramaic', 'aii'),
    ('Basque', 'eus'),
    ('Catalan', 'cat'),
    ('Church Slavic', 'chu'),
    ('Classical Syriac', 'syc'),
    ('Coptic', 'cop'),
    ('Cornish', 'cor'),
    ('Croatian', 'hrv'),
    ('Czech', 'ces'),
    ('Danish', 'dan'),
    ('Dutch', 'nld'),
    ('Eastern Frisian', 'frs'),
    ('English', 'eng'),
    ('French', 'fra'),
    ('German', 'deu'),
    ('Hebrew', 'heb'),
    ('Hungarian', 'hun'),
    ('Irish', 'gle'),
    ('Italian', 'ita'),
    ('Latin', 'lat'),
    ('Low German', 'nds'),
    ('Official Aramaic (700-300 BCE)', 'arc'),
    ('Old French', 'fro'),
    ('Old Turkish', 'otk'),
    ('Persian', 'fas'),
    ('Polish', 'pol'),
    ('Portuguese', 'por'),
    ('Russian', 'rus'),
    ('Scots', 'sco'),
    ('Scottish Gaelic', 'gla'),
    ('Spanish', 'spa'),
    ('Swedish', 'swe'),
    ('Syriac', 'syr'),
    ('Tamil', 'tam'),
    ('Turkish', 'tur'),
    ('Welsh', 'cym'),
]

name_code_dict = dict(language_choices)

code_name_dict = {code: name for name, code in name_code_dict.items()}


class LangModelAdapter:

    def create_instance_by_owner_id(self, owner_id):
        raise NotImplementedError()


def create_lang_formset(lang_models: Iterable, lang_rec_id_name: str,
                        request_data=None, prefix='lang', extra=0):
    initial_list = model_utils.models_to_dict_list(lang_models)
    initial_list = list(initial_list)
    for initial in initial_list:
        initial['lang_name'] = code_name_dict.get(initial['language_code_id'],
                                                  'Unknown Language')
        initial['lang_rec_id'] = initial[lang_rec_id_name]

    return view_utils.create_formset(
        LangForm,
        post_data=request_data or None,
        prefix=prefix,
        extra=extra,
        initial_list=initial_list
    )


class LangForm(forms.Form):
    notes = forms.CharField(required=False)
    lang_name = forms.CharField(required=False, widget=forms.HiddenInput())
    is_del = form_utils.ZeroOneCheckboxField(is_str=False)
    lang_rec_id = forms.IntegerField(required=False, widget=forms.HiddenInput())


def add_new_lang_record(note_list: Iterable[str], lang_name_list: Iterable[str],
                        owner_id, lang_model_adapter: "LangModelAdapter"):
    lang_code_map = name_code_dict
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

        if lang_form.cleaned_data['is_del']:
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
