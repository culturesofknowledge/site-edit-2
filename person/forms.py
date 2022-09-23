import logging

from django import forms
from django.forms import ModelForm, CharField

from core.helper import form_utils, widgets_utils
from person.models import CofkUnionPerson

log = logging.getLogger(__name__)

calendar_date_choices = [
    ("", 'Unknown'),
    ("G", 'Gregorian'),
    ("JM", 'Julian (year starting 25th Mar)'),
    ("JJ", 'Julian (year starting 1st Jan)'),
    ("O", 'Other'),
]

person_gender_choices = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('', 'Unknown or not applicable'),
]


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


class PersonForm(ModelForm):
    gender = CharField(required=False,
                       widget=forms.RadioSelect(choices=person_gender_choices))

    is_organisation = YesEmptyCheckboxField()
    roles_titles = forms.CharField(required=False,
                                   widget=forms.CheckboxSelectMultiple(
                                       choices=[
                                           ('5', 'Antiquary'),
                                           ('28', 'Astrologer'),
                                           ('1', 'Astronomer'),
                                           ('8', 'Biographer'),
                                           ('15', 'Bookseller'),
                                           ('17', 'Classicist'),
                                           ('3', 'Cleric'),
                                           ('19', 'Diplomat'),
                                           ('10', 'Educational Theorist'),
                                           ('26', 'Freemason'),
                                           ('20', 'Keeper'),
                                           ('18', 'Lawyer'),
                                           ('24', 'Letter Carrier'),
                                           ('12', 'Linguist'),
                                           ('6', 'Mathematician'),
                                           ('16', 'Merchant'),
                                           ('22', 'Musician'),
                                           ('7', 'Natural Historian'),
                                           ('9', 'Naturalist'),
                                           ('23', 'Nonjuror'),
                                           ('27', 'Philosopher'),
                                           ('13', 'Physician'),
                                           ('2', 'Politician'),
                                           ('25', 'Printer'),
                                           ('14', 'Scholar'),
                                           ('21', 'Soldier'),
                                           ('4', 'Theologian'),
                                           ('11', 'Writer'),
                                       ]
                                   )
                                   )

    date_of_birth_year = form_utils.create_year_field()
    date_of_birth_month = form_utils.create_month_field()
    date_of_birth_day = form_utils.create_day_field()
    date_of_birth_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))

    date_of_death_year = form_utils.create_year_field()
    date_of_death_month = form_utils.create_month_field()
    date_of_death_day = form_utils.create_day_field()
    date_of_death_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))

    flourished_year = form_utils.create_year_field()
    flourished_month = form_utils.create_month_field()
    flourished_day = form_utils.create_day_field()
    flourished_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_calendar = forms.CharField(required=False,
                                          widget=forms.RadioSelect(choices=calendar_date_choices, ))

    birth_place = forms.CharField(required=False, widget=forms.HiddenInput())
    death_place = forms.CharField(required=False, widget=forms.HiddenInput())
    other_place = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = CofkUnionPerson
        fields = (
            'foaf_name',
            'gender',
            'is_organisation',
            'editors_notes',
            'skos_altlabel',
            'person_aliases',

            'date_of_birth_year',
            'date_of_birth_month',
            'date_of_birth_day',
            'date_of_birth',
            'date_of_birth_inferred',
            'date_of_birth_uncertain',
            'date_of_birth_approx',
            'date_of_birth_calendar',

            'date_of_death_year',
            'date_of_death_month',
            'date_of_death_day',
            'date_of_death',
            'date_of_death_inferred',
            'date_of_death_uncertain',
            'date_of_death_approx',

            'flourished_year',
            'flourished_month',
            'flourished_day',
            'flourished',
            'flourished_inferred',
            'flourished_uncertain',
            'flourished_approx',

            'further_reading',

            'date_of_birth_is_range',
            'date_of_death_is_range',
            'flourished_is_range',

        )

    def clean(self):
        log.debug(f'cleaned_data: {self.cleaned_data}')
        form_utils.clean_by_default_value(self.cleaned_data, [
            'date_of_birth_inferred',
            'date_of_birth_uncertain',
            'date_of_birth_approx',
            'date_of_death_inferred',
            'date_of_death_uncertain',
            'date_of_death_approx',
            'flourished_inferred',
            'flourished_uncertain',
            'flourished_approx',

            'date_of_birth_is_range',
            'date_of_death_is_range',
            'flourished_is_range',
        ], 0)

        return super().clean()


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'person/component/person_search_fieldset.html'

    iperson_id = forms.IntegerField(required=False)
    iperson_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    foaf_name = forms.CharField(required=False)
    foaf_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    birth_year_from = form_utils.create_year_field()
    birth_year_to = form_utils.create_year_field()

    death_year_from = form_utils.create_year_field()
    death_year_to = form_utils.create_year_field()

    flourished_year_from = form_utils.create_year_field()
    flourished_year_to = form_utils.create_year_field()

    gender = forms.CharField(required=False, widget=forms.Select(
        choices=[
            (None, 'All'),
            ('M', 'Male'),
            ('F', 'Female'),
            ('U', 'Unknown or not applicable'),
        ]
    ))

    person_or_group = forms.CharField(required=False, widget=forms.Select(choices=[
        (None, 'All'),
        ('P', 'Person'),
        ('G', 'Group'),
    ]))

    editors_notes = forms.CharField(required=False)
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    further_reading = forms.CharField(required=False)
    further_reading_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    change_timestamp_from = forms.DateField(required=False, widget=widgets_utils.NewDateInput())
    change_timestamp_to = forms.DateField(required=False, widget=widgets_utils.NewDateInput())

    change_user = forms.CharField(required=False)
    change_user_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
