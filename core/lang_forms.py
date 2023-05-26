from django import forms

from core.form_label_maps import field_label_map
from core.helper import form_utils
from core.helper.form_utils import BasicSearchFieldset, SearchCharField, SearchIntField

search_is_favorite_choices = [
    (None, 'Any'),
    (1, 'Yes'),
    (0, 'No'),
]


class LangSearchFieldset(BasicSearchFieldset):
    title = 'Language'
    template_name = 'core/component/lang_search_fieldset.html'

    code_639_3 = SearchCharField(
        label=field_label_map['lang']['code_639_3'],
        help_text='E.g. eng for English')
    code_639_3_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
    code_639_1 = SearchCharField(
        label=field_label_map['lang']['code_639_1'],
        help_text="E.g. en for English. Only the more widely-spoken languages have 2-letter codes. "
                  "To get a list of languages with 2-letter codes, click the Advanced Search button, "
                  "then choose 'Is not blank' from the dropdown list next to the 'Alternative 2-letter code' field.")
    code_639_1_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
    language_name = SearchCharField(
        label=field_label_map['lang']['language_name'],
        help_text='English, French, Arabic, etc. The name may be anglicised, '
                  'e.g. Persian rather than Farsi.')
    language_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    is_favorite = SearchCharField(
        help_text="""
The 'Favourite? ' field contains the word 'Yes' if this language has been selected for use in your project. Only selected languages will appear in data entry screens.
For example, you might select just English, French and Spanish from the thousands of potential languages listed here. You will then be offered the choice of just French, English and Spanish if you need to enter the language in which a work was composed.
You can return to the list of languages to make further selections whenever required, and your additional selections will then appear within data entry screens elsewhere in the system.
        """.strip(),
        widget=forms.Select(choices=search_is_favorite_choices))
