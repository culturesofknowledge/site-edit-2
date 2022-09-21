from django import forms
from django.forms import ModelForm, HiddenInput, IntegerField, CharField

from location.models import CofkUnionLocation


class LocationForm(ModelForm):
    form_title__ = 'Core fields and editors\' notes:'

    location_id = IntegerField(required=False, widget=HiddenInput())
    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs=dict(readonly=True)),
                              label='Full name of location')
    editors_notes = CharField(required=False,
                              widget=forms.Textarea())
    element_1_eg_room = CharField(required=False,
                                  label='1. E.g. room')
    element_2_eg_building = CharField(required=False,
                                      label='2. E.g. building')
    element_3_eg_parish = CharField(required=False,
                                    label='3. E.g. parish')
    element_4_eg_city = CharField(required=True,
                                  label='4. E.g. city * ')
    element_5_eg_county = CharField(required=False,
                                    label='5. E.g. county')
    element_6_eg_country = CharField(required=False,
                                     label='6. E.g. country')
    element_7_eg_empire = CharField(required=False,
                                    label='7. E.g. empire')
    location_synonyms = CharField(required=False,
                                  label='Alternative names for location')
    latitude = CharField(required=False)
    longitude = CharField(required=False)

    class Meta:
        model = CofkUnionLocation
        fields = (
            'location_id',
            'editors_notes',
            'element_1_eg_room', 'element_2_eg_building',
            'element_3_eg_parish', 'element_4_eg_city', 'element_5_eg_county',
            'element_6_eg_country', 'element_7_eg_empire',
            'location_name',
            'location_synonyms',
            'latitude', 'longitude',
        )


class GeneralSearchFieldset(forms.Form):
    title = 'General'
    template_name = 'core/form/search_fieldset.html'

    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'xxxx'}),
                              label='Full name of location')
    location_synonyms = forms.CharField(required=False,
                                        label='Alternative names for location', )
    location_id = IntegerField(required=False, label='Location id')
    editors_notes = CharField(required=False)
    latitude = IntegerField(required=False, label='Latitude')
    longitude = IntegerField(required=False, label='Longitude')
    element_1_eg_room = CharField(required=False, label='1. E.g. room')
    element_2_eg_building = CharField(required=False, label='2. E.g. building')
    element_3_eg_parish = CharField(required=False, label='3. E.g. parish')
    element_4_eg_city = CharField(required=False, label='4. E.g. city')
    element_5_eg_county = CharField(required=False, label='5. E.g. county')
    element_6_eg_country = CharField(required=False, label='6. E.g. country')
    element_7_eg_empire = CharField(required=False, label='7. E.g. empire')
