# Create your tests here.
from selenium.webdriver.common.by import By

from location.models import CofkCollectLocation
from siteedit2.utils.test_utils import EmloSeleniumTestCase


class LocationFormTests(EmloSeleniumTestCase):

    def test_create_location(self):
        from django.conf import settings
        self.assertIn('pycharm-py', settings.ALLOWED_HOSTS)
        url = self.live_server_url + '/location/get-location'
        self.selenium.get(url)

        id_text_dict = dict(
            id_location_name='id_location_name value',
            id_element_1_eg_room='id_element_1_eg_room value',
            id_element_2_eg_building='id_element_2_eg_building value',
            id_element_3_eg_parish='id_element_3_eg_parish value',
            id_element_4_eg_city='id_element_4_eg_city value',
            id_element_5_eg_county='id_element_5_eg_county value',
            id_element_6_eg_country='id_element_6_eg_country value',
            id_element_7_eg_empire='id_element_7_eg_empire value',
            id_notes_on_place='id_notes_on_place value',
            id_editors_notes='id_editors_notes value',
            id_upload_name='id_upload_name value',
            id_location_synonyms='id_location_synonyms value',
            id_latitude='id_latitude value',
            id_longitude='id_longitude value',
        )
        for ele_id, text in id_text_dict.items():
            ele = self.selenium.find_element(value=ele_id)
            ele.send_keys(text)

        org_location_size = CofkCollectLocation.objects.count()

        submit_btn = self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]')
        submit_btn.click()

        self.assertGreater(CofkCollectLocation.objects.count(), org_location_size)
