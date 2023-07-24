import logging
from typing import Iterable

from django import forms

from core.helper import model_serv, form_serv, widgets_serv
from core.models import Iso639LanguageCode

log = logging.getLogger(__name__)


class LangModelAdapter:

    def create_instance_by_owner_id(self, owner_id):
        raise NotImplementedError()


def create_lang_formset(lang_models: Iterable, lang_rec_id_name: str,
                        request_data=None, prefix='lang', extra=0):
    initial_list = model_serv.models_to_dict_list(lang_models)
    initial_list = list(initial_list)
    for initial in initial_list:
        initial['lang_name'] = (Iso639LanguageCode.objects
                                .filter(code_639_3=initial['language_code_id'])
                                .values_list('language_name', flat=True)
                                .first() or f'Unknown Language [{initial["language_code_id"]}]')
        initial['lang_rec_id'] = initial[lang_rec_id_name]

    return form_serv.create_formset(
        LangForm,
        post_data=request_data or None,
        prefix=prefix,
        extra=extra,
        initial_list=initial_list
    )


class LangForm(forms.Form):
    notes = forms.CharField(required=False)
    lang_name = forms.CharField(required=False, widget=forms.HiddenInput())
    is_delete = form_serv.DeleteCheckboxField()
    lang_rec_id = forms.IntegerField(required=False, widget=forms.HiddenInput())


class NewLangForm(forms.Form):
    new_language = forms.CharField(required=False, widget=forms.TextInput({
        'list': 'id_language_list',
    }))

    language_list = forms.Field(required=False, widget=widgets_serv.Datalist(choices=[]))

    def remove_selected_lang_choices(self, selected_langs: Iterable):
        choices = self.fields['language_list'].widget.choices
        selected_codes = {l.language_code_id for l in selected_langs}
        new_choices = [c for c in choices if c[1] not in selected_codes]
        new_choices = sorted(new_choices)
        self.fields['language_list'].widget.choices = new_choices

    @classmethod
    def create_new_lang_form(cls, selected_langs: Iterable = None):
        form = cls()
        language_choices = convert_lang_queryset_to_dict(
            Iso639LanguageCode.objects.filter(cofkunionfavouritelanguage__isnull=False))
        form.fields['language_list'].widget.choices = sorted(language_choices.items())
        if selected_langs is not None:
            form.remove_selected_lang_choices(selected_langs)
        return form


def add_new_lang_record(note_list: Iterable[str], lang_name_list: Iterable[str],
                        owner_id, lang_model_adapter: "LangModelAdapter"):
    lang_name_list = list(lang_name_list)
    lang_code_map = convert_lang_queryset_to_dict(Iso639LanguageCode.objects.filter(language_name__in=lang_name_list))
    for _name in lang_name_list:
        if _name not in lang_code_map:
            raise ValueError(f'unexpected language name [{_name}]')

    lang_code_list = (lang_code_map[n] for n in lang_name_list)
    for note, code in zip(note_list, lang_code_list):
        lang = lang_model_adapter.create_instance_by_owner_id(owner_id)
        lang.language_code_id = code
        lang.notes = note
        lang.save()


def convert_lang_queryset_to_dict(queryset) -> dict[str, str]:
    return dict(queryset.values_list('language_name', 'code_639_3').all())


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
