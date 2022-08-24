from django import forms
from django.forms import ModelForm, CharField

from core.helper import widgets_utils
from person.models import CofkUnionPerson


class PersonForm(ModelForm):
    # location_id = IntegerField(required=False, widget=HiddenInput())
    # location_name = CharField(required=False,
    #                           widget=forms.TextInput(attrs=dict(readonly=True)),
    #                           label='Full name of location')
    # editors_notes = CharField(required=False,
    #                           widget=forms.Textarea())
    # element_1_eg_room = CharField(required=False,
    #                               label='1. E.g. room')
    # element_2_eg_building = CharField(required=False,
    #                                   label='2. E.g. building')
    # element_3_eg_parish = CharField(required=False,
    #                                 label='3. E.g. parish')
    # element_4_eg_city = CharField(required=True,
    #                               label='4. E.g. city')
    # element_5_eg_county = CharField(required=False,
    #                                 label='5. E.g. county')
    # element_6_eg_country = CharField(required=False,
    #                                  label='6. E.g. country')
    # element_7_eg_empire = CharField(required=False,
    #                                 label='7. E.g. empire')
    # location_synonyms = CharField(required=False,
    #                               label='Alternative names for location')
    # latitude = CharField(required=False)
    # longitude = CharField(required=False)

    gender = CharField(required=False,
                       widget=forms.RadioSelect(choices=[
                           ('M', 'Male'),
                           ('F', 'Female'),
                           ('', 'Unknown or not applicable'),
                       ])
                       )
    is_organisation = forms.BooleanField(required=False,
                                         widget=widgets_utils.create_common_checkbox(value='1'),
                                         initial='1',
                                         )
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
            'date_of_death_year',
            'date_of_death_month',
            'date_of_death_day',
            'date_of_death',
            'date_of_death_inferred',
            'date_of_death_uncertain',
            'date_of_death_approx',

            'further_reading',
        )


"""
"""
