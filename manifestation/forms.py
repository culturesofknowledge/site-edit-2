from django import forms

from core.form_label_maps import field_label_map
from core.helper import form_serv
from core.helper.form_serv import SearchCharField, SearchIntField
from work.forms import manif_type_choices


class ManifSearchFieldset(form_serv.BasicSearchFieldset):
    title = 'General'
    template_name = 'manif/component/manif_search_fieldset.html'

    work_id = SearchIntField(min_value=1, label=field_label_map['manif']['work_id'],
                             help_text='The Work ID associated with the manifestation.')
    work_id_lookup = form_serv.create_lookup_field(form_serv.IntLookupChoices.choices)

    manifestation_type = forms.CharField(
        required=False,
        label=field_label_map['manif']['manifestation_type'],
        widget=forms.Select(choices=[('', '---------')] + manif_type_choices,
                            attrs={'class': 'searchfield'}),
    )

    id_number_or_shelfmark = SearchCharField(
        label=field_label_map['manif']['id_number_or_shelfmark'],
        help_text='The shelfmark or ID number of the manifestation.')
    id_number_or_shelfmark_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)
