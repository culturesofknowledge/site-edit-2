from django import forms

from core.form_label_maps import field_label_map
from core.helper.form_serv import SearchCharField, create_lookup_field, StrLookupChoices, SearchIntField, \
    IntLookupChoices, BasicSearchFieldset
from core.helper.widgets_serv import SearchDateTimeInput
from uploader.models import CofkCollectUpload, CofkCollectWork

excelMimeTypes = ".xls," \
                 ".xlsx," \
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet," \
                 "application/vnd.ms-excel"


class CofkCollectUploadForm(forms.ModelForm):
    class Meta:
        model = CofkCollectUpload
        fields = ('upload_file', )
        widgets = {
            'upload_file': forms.FileInput(attrs={'accept': excelMimeTypes,
                                                  'class': 'btn'})
        }


class CofkCollectWorkForm(forms.ModelForm):
    class Meta:
        model = CofkCollectWork
        fields = '__all__'

source_help_text = 'The name of the researcher who contributed the data, followed by the date and' \
                   ' time when the contribution was uploaded.'

status_choices = [
    ('Awaiting review','Awaiting review'),
    ('Partly reviewed','Partly reviewed'),
    ('Review complete','Review complete'),
    ('Accepted and saved into main database','Accepted and saved into main database'),
    ('Rejected','Rejected'),
    ('',''),
]

calendar_choices = [('j', 'Julian'), ('g', 'Gregorian'), ('', 'Unknown')]

class GeneralSearchFieldset(BasicSearchFieldset):
    title = 'General'
    template_name = 'uploader/component/collectwork_search_fieldset.html'

    source = SearchCharField(help_text=source_help_text)
    source_lookup = create_lookup_field(StrLookupChoices.choices)

    contact = SearchCharField(help_text='Email address of contributor.')
    contact_lookup = create_lookup_field(StrLookupChoices.choices)

    status = SearchCharField(widget=forms.Select(choices=status_choices))

    id_main = SearchCharField(label=field_label_map['collect_work']['id_main'],
                              help_text='Unique work ID as saved in EMLO-edit. '
                                        'Blank for works which have not been accepted.')
    id_main_lookup = create_lookup_field(StrLookupChoices.choices)

    editors_notes = SearchCharField(label=field_label_map['collect_work']['editors_notes'],
                                    help_text='Notes for internal use, intended to hold temporary queries etc.')
    editors_notes_lookup = create_lookup_field(StrLookupChoices.choices)

    date_of_work_std_year = SearchIntField(min_value=1000, max_value=1850,
                                           label=field_label_map['collect_work']['date_of_work_std_year'])
    date_of_work_std_year_lookup = create_lookup_field(IntLookupChoices.choices)

    date_of_work_std_month = SearchIntField(min_value=1, max_value=12,
                                            label=field_label_map['collect_work']['date_of_work_std_month'])
    date_of_work_std_month_lookup = create_lookup_field(IntLookupChoices.choices)

    date_of_work_std_day = SearchIntField(min_value=1, max_value=31,
                                          label=field_label_map['collect_work']['date_of_work_std_day'])
    date_of_work_std_day_lookup = create_lookup_field(IntLookupChoices.choices)

    date_of_work_std_from = forms.DateField(required=False,
                                            widget=SearchDateTimeInput(attrs={'class': 'searchfield'}))
    date_of_work_std_to = forms.DateField(required=False,
                                          widget=SearchDateTimeInput(attrs={'class': 'searchfield'}))

    date_of_work_as_marked = SearchCharField()
    date_of_work_as_marked_lookup = create_lookup_field(StrLookupChoices.choices)

    original_calendar = SearchCharField(widget=forms.Select(choices=calendar_choices))

    notes_on_date_of_work = SearchCharField()
    notes_on_date_of_work_lookup = create_lookup_field(StrLookupChoices.choices)

    authors = SearchCharField()
    authors_lookup = create_lookup_field(StrLookupChoices.choices)

    authors_as_marked = SearchCharField()
    authors_as_marked_lookup = create_lookup_field(StrLookupChoices.choices)

    notes_on_authors = SearchCharField()
    notes_on_authors_lookup = create_lookup_field(StrLookupChoices.choices)

    origin = SearchCharField()
    origin_lookup = create_lookup_field(StrLookupChoices.choices)

    origin_as_marked = SearchCharField()
    origin_as_marked_lookup = create_lookup_field(StrLookupChoices.choices)

    addressees = SearchCharField()
    addressees_lookup = create_lookup_field(StrLookupChoices.choices)

    addressees_as_marked = SearchCharField()
    addressees_as_marked_lookup = create_lookup_field(StrLookupChoices.choices)

    notes_on_addressees = SearchCharField()
    notes_on_addressees_lookup = create_lookup_field(StrLookupChoices.choices)

    upload_id = SearchIntField()
    upload_id_lookup = create_lookup_field(IntLookupChoices.choices)

    destination = SearchCharField()
    destination_lookup = create_lookup_field(StrLookupChoices.choices)

    destination_as_marked = SearchCharField()
    destination_as_marked_lookup = create_lookup_field(StrLookupChoices.choices)

    manifestations = SearchCharField()
    manifestations_lookup = create_lookup_field(StrLookupChoices.choices)

    abstract = SearchCharField()
    abstract_lookup = create_lookup_field(StrLookupChoices.choices)

    keywords = SearchCharField()
    keywords_lookup = create_lookup_field(StrLookupChoices.choices)

    languages = SearchCharField()
    languages_lookup = create_lookup_field(StrLookupChoices.choices)

    subjects = SearchCharField()
    subjects_lookup = create_lookup_field(StrLookupChoices.choices)

    incipit = SearchCharField()
    incipit_lookup = create_lookup_field(StrLookupChoices.choices)

    excipit = SearchCharField()
    excipit_lookup = create_lookup_field(StrLookupChoices.choices)

    people_mentioned = SearchCharField()
    people_mentioned_lookup = create_lookup_field(StrLookupChoices.choices)

    notes_on_people_mentioned = SearchCharField()
    notes_on_people_mentioned_lookup = create_lookup_field(StrLookupChoices.choices)

    places_mentioned = SearchCharField()
    places_mentioned_lookup = create_lookup_field(StrLookupChoices.choices)

    notes_on_letter = SearchCharField()
    notes_on_letter_lookup = create_lookup_field(StrLookupChoices.choices)

    resources = SearchCharField(label=field_label_map['collect_work']['resources'])
    resources_lookup = create_lookup_field(StrLookupChoices.choices)
