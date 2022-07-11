from django.forms import ModelForm, HiddenInput, IntegerField

from location.models import CofkUnionLocation, CofkCollectLocationResource


class LocationForm(ModelForm):
    location_id = IntegerField(required=False)
    location_id.widget = HiddenInput()

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
        model = CofkCollectLocationResource
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
