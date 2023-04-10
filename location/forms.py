from django import forms
from django.forms import ModelForm, HiddenInput, CharField, IntegerField

from core.helper import form_utils
from core.helper.form_utils import SearchCharField, SearchIntField
from location.models import CofkUnionLocation


class LocationForm(ModelForm):
    form_title__ = 'Core fields and editors\' notes'

    location_id = IntegerField(required=False, widget=HiddenInput())
    location_name = CharField(required=False,
                              widget=forms.TextInput(attrs=dict(readonly=True)),
                              label='Full name of location')
    editors_notes = form_utils.CommonTextareaField()
    element_1_eg_room = CharField(required=False, label='1. E.g. room')
    element_2_eg_building = CharField(required=False, label='2. E.g. building')
    element_3_eg_parish = CharField(required=False, label='3. E.g. parish')
    element_4_eg_city = CharField(required=False, label='4. E.g. city')
    element_5_eg_county = CharField(required=False, label='5. E.g. county')
    element_6_eg_country = CharField(required=False, label='6. E.g. country')
    element_7_eg_empire = CharField(required=False, label='7. E.g. empire')
    location_synonyms = form_utils.CommonTextareaField(required=False, label='Alternative names for location')
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


field_label_map = { 'location_name': 'Name',
                    'location_id': 'Location id',
                    'editors_notes': 'Editors\' notes',
                    'sent': 'Sent',
                    'recd': 'Received',
                    'all_works': 'Sent and received',
                    'researchers_notes': 'Researchers\' notes',
                    'resources': 'Related resources',
                    'latitude': 'Latitude',
                    'longitude': 'Longitude',
                    'publication_id': 'Publication id',
                    'element_1_eg_room': '1. E.g. room',
                    'element_2_eg_building': '2. E.g. building',
                    'element_3_eg_parish': '3. E.g. parish',
                    'element_4_eg_city': '4. E.g. city',
                    'element_5_eg_county': '5. E.g. county',
                    'element_6_eg_country': '6. E.g. country',
                    'element_7_eg_empire': '7. E.g. empire',
                    'images': 'Images',
                    'change_user': 'Last edited by',
                    }

class GeneralSearchFieldset(form_utils.BasicSearchFieldset):
    title = 'General'
    template_name = 'location/component/location_search_fieldset.html'

    location_name = SearchCharField(label='Name',
                              help_text='This field contains the primary name and'
                                        ' any alternative names for a location.')
    location_name_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    location_id = SearchIntField(help_text='The unique ID for the record within this database.')
    location_id_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    editors_notes = SearchCharField(label='Editors\' notes',
                              help_text='Notes for internal use. Not intended for front-end display.')
    editors_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    sent = SearchIntField(help_text="Number of letters sent from this place of origin."
                                    " You can search on these 'number' fields using 'Advanced Search', e.g. you could"
                                    " enter something like 'Sent greater than 100' to identify a place from which many"
                                    " letters were sent, but please note that these will be slower searches than those"
                                    " on place name or latitude/longitude.")
    sent_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    recd = SearchIntField(label='Received',
                            help_text='Number of letters sent to this destination.')
    recd_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    all_works = SearchIntField(label='Sent and received',
                                 help_text='Total number of letters sent to and from this place.')
    all_works_lookup = form_utils.create_lookup_field(form_utils.IntLookupChoices.choices)

    researchers_notes = SearchCharField(label='Researchers\' notes',
                                  help_text='Comments destined for front-end display.')
    researchers_notes_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    resources = SearchCharField(label='Related resources')
    resources_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    latitude = SearchCharField()
    latitude_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    longitude = SearchCharField()
    longitude_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_1_eg_room = SearchCharField(label='1. E.g. room',
                                  help_text="'Sub-place', e.g. Porter's Lodge")
    element_1_eg_room_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_2_eg_building = SearchCharField(label='2. E.g. building',
                                      help_text="'Place', e.g. St Anne's College")
    element_2_eg_building_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_3_eg_parish = SearchCharField(label='3. E.g. parish',
                                    help_text="Civil parish/township', e.g. University of Oxford")
    element_3_eg_parish_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_4_eg_city = SearchCharField(label='4. E.g. city',
                                  help_text="'Local administrative unit' (city or town), e.g. Oxford")
    element_4_eg_city_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_5_eg_county = SearchCharField(label='5. E.g. county',
                                    help_text="'Wider administrative unit', e.g. Oxfordshire")
    element_5_eg_county_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_6_eg_country = SearchCharField(label='6. E.g. country',
                                     help_text="'Country', e.g. England")
    element_6_eg_country_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    element_7_eg_empire = SearchCharField(label='7. E.g. empire',
                                    help_text="'Nation', e.g. United Kingdom")
    element_7_eg_empire_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)

    images = SearchCharField()
    images_lookup = form_utils.create_lookup_field(form_utils.StrLookupChoices.choices)
