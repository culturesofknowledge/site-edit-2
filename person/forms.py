import logging

from django import forms
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


# def calendar_date


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

    date_of_birth_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_birth_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))
    date_of_birth_date = form_utils.ThreeFieldDateField(
        'date_of_birth_year',
        'date_of_birth_month',
        'date_of_birth_day',
    )

    date_of_death_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    date_of_death_calendar = forms.CharField(required=False,
                                             widget=forms.RadioSelect(choices=calendar_date_choices, ))
    date_of_death_date = form_utils.ThreeFieldDateField(
        'date_of_death_year',
        'date_of_death_month',
        'date_of_death_day',
    )

    flourished_inferred = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_uncertain = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_approx = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_is_range = form_utils.ZeroOneCheckboxField(is_str=False, initial=0)
    flourished_calendar = forms.CharField(required=False,
                                          widget=forms.RadioSelect(choices=calendar_date_choices, ))
    flourished_date = form_utils.ThreeFieldDateField(
        'flourished_year',
        'flourished_month',
        'flourished_day',
    )

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

        for field_name in form_utils.filter_and_log_field_names(
                self.cleaned_data, ['date_select_birth']):
            self.fields[field_name].clean_other_fields(self.cleaned_data, self.cleaned_data.get(field_name))

        return super().clean()
