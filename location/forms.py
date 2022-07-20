from django import forms
from django.forms import ModelForm, HiddenInput, IntegerField, CharField

from core.models import CofkUnionResource, CofkUnionComment
from location.models import CofkUnionLocation


def create_common_text_input(**attrs):
    _attrs = {'class': 'formtext'} | (attrs or {})
    return forms.TextInput(_attrs)


class LocationForm(ModelForm):
    location_id = IntegerField(required=False, widget=HiddenInput())
    location_name = CharField(required=False,
                              widget=create_common_text_input(readonly=True))
    editors_notes = CharField(required=False,
                              widget=forms.Textarea())
    element_1_eg_room = CharField(required=False, widget=create_common_text_input())
    element_2_eg_building = CharField(required=False, widget=create_common_text_input())
    element_3_eg_parish = CharField(required=False, widget=create_common_text_input())
    element_4_eg_city = CharField(required=True, widget=create_common_text_input())
    element_5_eg_county = CharField(required=False, widget=create_common_text_input())
    element_6_eg_country = CharField(required=False, widget=create_common_text_input())
    element_7_eg_empire = CharField(required=False, widget=create_common_text_input())
    location_synonyms = CharField(required=False, widget=create_common_text_input())
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
        labels = {
            'element_1_eg_room': '1. E.g. room',
            'element_2_eg_building': '2. E.g. building',
            'element_3_eg_parish': '3. E.g. parish',
            'element_4_eg_city': '4. E.g. city',
            'element_5_eg_county': '5. E.g. county',
            'element_6_eg_country': '6. E.g. country',
            'element_7_eg_empire': '7. E.g. empire',
            'location_name': 'Full name of location',
            'location_synonyms': 'Alternative names for location',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
        }


class LocationResourceForm(ModelForm):
    resource_id = IntegerField(required=False)
    resource_id.widget = HiddenInput()

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
