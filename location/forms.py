from django import forms
from django.forms import ModelForm, HiddenInput, IntegerField, CharField

from core.helper import form_utils
from location.models import CofkUnionLocation


class LocationForm(ModelForm):
    form_title__ = 'Core fields and editors\' notes'

    location_id = IntegerField(required=False, widget=HiddenInput())
    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs=dict(readonly=True)),
                              label='Full name of location')
    editors_notes = form_utils.CommonTextareaField()
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
    template_name = 'location/component/location_search_fieldset.html'

    location_name = CharField(required=False,
                              label='Full name of location')
    location_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    location_synonyms = forms.CharField(required=False,
                                        label='Alternative names for location', )
    location_synonyms_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    location_id = IntegerField(required=False, label='Location id')
    location_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    editors_notes = CharField(required=False)
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    latitude = IntegerField(required=False, label='Latitude')
    latitude_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    longitude = IntegerField(required=False, label='Longitude')
    longitude_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    element_1_eg_room = CharField(required=False, label='1. E.g. room')
    element_1_eg_room_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_2_eg_building = CharField(required=False, label='2. E.g. building')
    element_2_eg_building_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_3_eg_parish = CharField(required=False, label='3. E.g. parish')
    element_3_eg_parish_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_4_eg_city = CharField(required=False, label='4. E.g. city')
    element_4_eg_city_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_5_eg_county = CharField(required=False, label='5. E.g. county')
    element_5_eg_county_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_6_eg_country = CharField(required=False, label='6. E.g. country')
    element_6_eg_country_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_7_eg_empire = CharField(required=False, label='7. E.g. empire')
    element_7_eg_empire_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
