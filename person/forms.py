import logging

from django import forms
from django.db.models import TextChoices
from django.forms import ModelForm, CharField

from core.helper import form_utils
from person.models import CofkUnionPerson

log = logging.getLogger(__name__)

calendar_date_choices = [
    ("", 'Unknown'),
    ("G", 'Gregorian'),
    ("JM", 'Julian (year starting 25th Mar)'),
    ("JJ", 'Julian (year starting 1st Jan)'),
    ("O", 'Other'),
]

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


def create_day_field(required=False):
    return forms.IntegerField(required=required, min_value=1, max_value=31)


def create_month_field(required=False):
    return forms.IntegerField(required=required,
                              widget=forms.Select(choices=short_month_choices))


def create_year_field(required=False):
    return forms.IntegerField(required=required, min_value=1, max_value=9999)


class PersonForm(ModelForm):
    gender = CharField(required=False,
                       widget=forms.RadioSelect(choices=[
                           ('M', 'Male'),
                           ('F', 'Female'),
                           ('', 'Unknown or not applicable'),
                       ])
                       )

    is_organisation = form_utils.ZeroOneCheckboxField(required=False, initial='1', )
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

    date_of_birth_year = create_year_field()
    date_of_birth_month = create_month_field()
    date_of_birth_day = create_day_field()
    date_of_birth_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))

    date_of_death_year = create_year_field()
    date_of_death_month = create_month_field()
    date_of_death_day = create_day_field()
    date_of_death_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))

    flourished_year = create_year_field()
    flourished_month = create_month_field()
    flourished_day = create_day_field()
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


class StrLookupChoices(TextChoices):
    CONTAINS = 'contains', 'contains',
    DOES_NOT_CONTAIN = 'does_not_contain', 'does not contain',

    STARTS_WITH = 'starts_with', 'starts with',
    DOES_NOT_START_WITH = 'does_not_start_with', 'does not start with',
    ENDS_WITH = 'ends_with', 'ends with',
    DOES_NOT_END_WITH = 'does_not_end_with', 'does not end with',

    EQUALS = 'equals', 'equals',
    IS_NOT_EQUAL_TO = 'is_not_equal_to', 'is not equal to',

    IS_BLANK = 'is_blank', 'is blank',
    IS_NOT_BLANK = 'is_not_blank', 'is not blank',


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'person/component/person_search_fieldset.html'

    # location_name = forms.CharField(required=False,
    #                           widget=forms.TextInput(attrs={'placeholder': 'xxxx'}))
    # location_id = forms.IntegerField(required=False)
    # editors_notes = forms.CharField(required=False)
    # latitude = forms.IntegerField(required=False)
    # longitude = forms.IntegerField(required=False)
    # element_1_eg_room = forms.CharField(required=False)
    # element_2_eg_building = forms.CharField(required=False)
    # element_3_eg_parish = forms.CharField(required=False)
    # element_4_eg_city = forms.CharField(required=False)
    # element_5_eg_county = forms.CharField(required=False)
    # element_6_eg_country = forms.CharField(required=False)
    # element_7_eg_empire = forms.CharField(required=False)

    iperson_id = forms.IntegerField(required=False)

    foaf_name = forms.CharField(required=False)
    foaf_name_lookup = CharField(required=False,
                                 widget=forms.Select(choices=StrLookupChoices.choices), )

    birth_year_from = create_year_field()
    birth_year_to = create_year_field()

    death_year_from = create_year_field()
    death_year_to = create_year_field()

    flourished_year_from = create_year_field()
    flourished_year_to = create_year_field()
