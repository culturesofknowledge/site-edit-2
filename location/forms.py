from django import forms
from django.forms import ModelForm, HiddenInput, IntegerField, CharField, Form

from core.models import CofkUnionResource, CofkUnionComment
from location.models import CofkUnionLocation
from siteedit2 import settings
from uploader.models import CofkUnionImage


def create_common_text_input(**attrs):
    _attrs = {'class': 'formtext'} | (attrs or {})
    return forms.TextInput(_attrs)


def create_common_checkbox(**attrs):
    _attrs = {'class': 'elcheckbox'} | (attrs or {})
    return forms.CheckboxInput(_attrs)


class LocationForm(ModelForm):
    location_id = IntegerField(required=False, widget=HiddenInput())
    location_name = CharField(required=False,
                              widget=create_common_text_input(readonly=True),
                              label='Full name of location')
    editors_notes = CharField(required=False,
                              widget=forms.Textarea())
    element_1_eg_room = CharField(required=False, widget=create_common_text_input(),
                                  label='1. E.g. room')
    element_2_eg_building = CharField(required=False, widget=create_common_text_input(),
                                      label='2. E.g. building')
    element_3_eg_parish = CharField(required=False, widget=create_common_text_input(),
                                    label='3. E.g. parish')
    element_4_eg_city = CharField(required=True, widget=create_common_text_input(),
                                  label='4. E.g. city')
    element_5_eg_county = CharField(required=False, widget=create_common_text_input(),
                                    label='5. E.g. county')
    element_6_eg_country = CharField(required=False, widget=create_common_text_input(),
                                     label='6. E.g. country')
    element_7_eg_empire = CharField(required=False, widget=create_common_text_input(),
                                    label='7. E.g. empire')
    location_synonyms = CharField(required=False, widget=create_common_text_input(),
                                  label='Alternative names for location')
    latitude = CharField(required=False, widget=create_common_text_input())
    longitude = CharField(required=False, widget=create_common_text_input())

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


class LocationResourceForm(ModelForm):
    resource_id = IntegerField(required=False, widget=HiddenInput())

    class Meta:
        model = CofkUnionResource
        fields = (
            # upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
            'resource_id',
            'resource_name',
            'resource_url',
            'resource_details',
        )
        labels = {
            'resource_name': 'Title or brief description',
            'resource_url': 'URL',
            'resource_details': 'Further details of resource',
        }


class LocationCommentForm(ModelForm):
    comment_id = IntegerField(required=False)
    comment_id.widget = HiddenInput()

    class Meta:
        model = CofkUnionComment
        fields = (
            'comment_id',
            'comment',
        )
        labels = {
            'comment': 'Note',
        }


class LocUploadImageForm(Form):
    image = forms.ImageField(required=False)


class LocationImageForm(ModelForm):
    image_id = IntegerField(required=False, widget=HiddenInput())
    image_filename = forms.CharField(required=False, widget=create_common_text_input(),
                                     label='URL for full-size image')
    thumbnail = forms.CharField(required=False, widget=create_common_text_input(),
                                label='URL for thumbnail (if any)')
    credits = forms.CharField(required=False, widget=create_common_text_input(),
                              label="Credits for 'front end' display*")
    licence_details = forms.CharField(required=False, widget=forms.Textarea(),
                                      label='Either: full text of licence*')
    licence_url = forms.CharField(required=False,
                                  label='licence URL*')
    licence_url.widget.attrs.update({'class': 'formtext url_checker',
                                     'value': settings.DEFAULT_IMG_LICENCE_URL})

    # KTODO
    # can_be_displayed = forms.BooleanField(required=False,
    #                                       label='Can be displayed to public',
    #                                       widget=create_common_checkbox(),
    #                                       initial=True,
    #                                       )
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
            # 'can_be_displayed',
            'display_order',
        )


class GeneralSearchFieldset(ModelForm):
    title = 'General'
    template_name = 'core/form/search_fieldset.html'

    location_id = IntegerField(required=False)
    editors_notes = CharField(required=False)
    location_synonyms = CharField(required=False)
    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'xxxx'}))

    class Meta:
        # KTODO to be cleanup
        model = CofkUnionLocation
        fields = (
            'location_id',
            'editors_notes',
            # 'element_1_eg_room', 'element_2_eg_building',
            # 'element_3_eg_parish', 'element_4_eg_city', 'element_5_eg_county',
            # 'element_6_eg_country', 'element_7_eg_empire',
            'location_name',
            'location_synonyms',
            # 'latitude', 'longitude',
        )
        labels = {
            # 'element_1_eg_room': '1. E.g. room',
            # 'element_2_eg_building': '2. E.g. building',
            # 'element_3_eg_parish': '3. E.g. parish',
            # 'element_4_eg_city': '4. E.g. city',
            # 'element_5_eg_county': '5. E.g. county',
            # 'element_6_eg_country': '6. E.g. country',
            # 'element_7_eg_empire': '7. E.g. empire',
            'location_id': 'Location id',
            'location_name': 'Full name of location',
            'location_synonyms': 'Alternative names for location',
            # 'latitude': 'Latitude',
            # 'longitude': 'Longitude',
        }
