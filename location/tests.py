# Create your tests here.

from selenium.webdriver.common.by import By

from location import fixtures
from location.models import CofkCollectLocation, CofkCollectLocationResource
from siteedit2.utils.test_utils import EmloSeleniumTestCase


class LocationFormTests(EmloSeleniumTestCase):

    def test_create_location(self):
        from django.conf import settings
        self.assertIn('pycharm-py', settings.ALLOWED_HOSTS)

        self.selenium.get(self.get_url_by_viewname('location:init_form'))

        self.fill_val_by_selector_list((f'#id_{k}', v)
                                       for k, v in fixtures.location_dict_a.items())

        org_location_size = CofkCollectLocation.objects.count()

        submit_btn = self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]')
        submit_btn.click()

        # check new location should be created in db
        self.assertGreater(CofkCollectLocation.objects.count(), org_location_size)

    def test_edit_location(self):
        loc_a = fixtures.create_location_a()
        loc_a.save()
        n_res = loc_a.resources.count()

        # check before update
        self.assertEqual(n_res, 0)

        # update web page
        url = self.get_url_by_viewname('location:full_form',
                                       kwargs={'location_id': loc_a.location_id})
        self.selenium.get(url)

        self.fill_val_by_selector_list((f'#id_loc_res-{n_res}-{k}', v)
                                       for k, v in fixtures.loc_res_dict_a.items())

        self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()

        # assert result after form submit
        loc_a.refresh_from_db()

        self.assertEqual(loc_a.resources.count(), 1)
        loc_res: CofkCollectLocationResource = loc_a.resources.first()
        self.assertEqual(loc_res.resource_name, fixtures.loc_res_dict_a['resource_name'])
