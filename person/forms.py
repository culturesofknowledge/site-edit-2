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

    def get_initial_for_field(self, field, field_name):
        if hasattr(field, 'get_initial_by_initial_dict'):
            return field.get_initial_by_initial_dict(field_name, self.initial)

        return super().get_initial_for_field(field, field_name)

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

        # trigger clean_other_fields
        _fields = ((n, f) for n, f in self.fields.items()
                   if hasattr(f, 'clean_other_fields'))
        for field_name, field in _fields:
            field.clean_other_fields(self.cleaned_data, self.cleaned_data.get(field_name))

        return super().clean()


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'core/form/search_fieldset.html'

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

    person_id = forms.IntegerField(required=False)
    foaf_name = forms.CharField(required=False)

    birth_year_from = forms.IntegerField(required=False)
    birth_year_to = forms.IntegerField(required=False)

    death_year_from = forms.IntegerField(required=False)
    death_year_to = forms.IntegerField(required=False)

    flourished_year_from = forms.IntegerField(required=False)
    flourished_year_to = forms.IntegerField(required=False)
