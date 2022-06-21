from django.forms import ModelForm, HiddenInput, IntegerField

from location.models import CofkCollectLocation


class LocationForm(ModelForm):
    # location_name = forms.CharField(label='Location name', max_length=100)
    location_id = IntegerField()
    location_id.widget = HiddenInput()

    class Meta:
        model = CofkCollectLocation
        fields = ('location_id',  'location_name',
                  'element_1_eg_room', 'element_2_eg_building',
                  'element_3_eg_parish', 'element_4_eg_city', 'element_5_eg_county',
                  'element_6_eg_country', 'element_7_eg_empire', 'notes_on_place',
                  'editors_notes', 'upload_name', 'location_synonyms',
                  'latitude', 'longitude',)
