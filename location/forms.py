from django import forms
from django.conf import settings
from django.forms import ModelForm, HiddenInput, IntegerField, CharField, Form

from core.helper import form_utils
from core.models import CofkUnionResource
from location.models import CofkUnionLocation
from uploader.models import CofkUnionImage


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


class LocUploadImageForm(Form):
    image = forms.ImageField(required=False)


class LocationImageForm(ModelForm):
    image_id = IntegerField(required=False, widget=HiddenInput())
    image_filename = forms.CharField(required=False,
                                     label='URL for full-size image')
    image_filename.widget.attrs.update({'class': 'url_checker'})

    thumbnail = forms.CharField(required=False,
                                label='URL for thumbnail (if any)')
    credits = forms.CharField(required=False,
                              label="Credits for 'front end' display*")
    licence_details = forms.CharField(required=False, widget=forms.Textarea(),
                                      label='Either: full text of licence*')

    licence_url = forms.CharField(required=False,
                                  label='licence URL*')
    licence_url.widget.attrs.update({'class': 'url_checker', 'value': settings.DEFAULT_IMG_LICENCE_URL})

    can_be_displayed = form_utils.ZeroOneCheckboxField(required=False,
                                                       label='Can be displayed to public',
                                                       initial='1', )
    display_order = forms.IntegerField(required=False, label='Order for display in front end')

    class Meta:
        model = CofkUnionImage
        fields = (
            'image_id',
            'image_filename',
            'thumbnail',
            'credits',
            'licence_details',
            'licence_url',
            'can_be_displayed',
            'display_order',
        )


class GeneralSearchFieldset(ModelForm):
    title = 'General'
    template_name = 'core/form/search_fieldset.html'

    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'xxxx'}))
    location_id = IntegerField(required=False)
    editors_notes = CharField(required=False)
    latitude = IntegerField(required=False)
    longitude = IntegerField(required=False)
    element_1_eg_room = CharField(required=False)
    element_2_eg_building = CharField(required=False)
    element_3_eg_parish = CharField(required=False)
    element_4_eg_city = CharField(required=False)
    element_5_eg_county = CharField(required=False)
    element_6_eg_country = CharField(required=False)
    element_7_eg_empire = CharField(required=False)

    class Meta:
        # KTODO to be cleanup
        model = CofkUnionLocation
        fields = (
            'location_name',
            'location_id',
            'editors_notes',
            # KTODO Sent, Rec'd, Sent or Rec'd
            # KTODO Researcher' notes
            # KTODO Related resources
            'latitude',
            'longitude',
            'element_1_eg_room',
            'element_2_eg_building',
            'element_3_eg_parish',
            'element_4_eg_city',
            'element_5_eg_county',
            'element_6_eg_country',
            'element_7_eg_empire',
            # KTODO Images
            # KTODO Last changed by
            # KTODO Last edit
        )
        labels = {
            'element_1_eg_room': '1. E.g. room',
            'element_2_eg_building': '2. E.g. building',
            'element_3_eg_parish': '3. E.g. parish',
            'element_4_eg_city': '4. E.g. city',
            'element_5_eg_county': '5. E.g. county',
            'element_6_eg_country': '6. E.g. country',
            'element_7_eg_empire': '7. E.g. empire',
            'location_id': 'Location id',
            'location_name': 'Full name of location',
            'location_synonyms': 'Alternative names for location',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
        }
        # KTODO Sent, Rec'd,  Sent or Rec'd, Images, Researchers' notes, Related resources
