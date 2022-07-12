# Create your tests here.

from selenium.webdriver.common.by import By

from location import fixtures
from location.models import CofkUnionLocation
from siteedit2.utils.test_utils import EmloSeleniumTestCase


class LocationFormTests(EmloSeleniumTestCase):

    def test_create_location(self):
        from django.conf import settings
        self.assertIn('pycharm-py', settings.ALLOWED_HOSTS)

        self.selenium.get(self.get_url_by_viewname('location:init_form'))

        self.fill_val_by_selector_list((f'#id_{k}', v)
                                       for k, v in fixtures.location_dict_a.items())

        org_location_size = CofkUnionLocation.objects.count()

        submit_btn = self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]')
        submit_btn.click()

        # check new location should be created in db
        self.assertGreater(CofkUnionLocation.objects.count(), org_location_size)

    def test_full_form__GET(self):
        loc_a = fixtures.create_location_a()
        loc_a.save()

        # update web page
        url = self.get_url_by_viewname('location:full_form',
                                       kwargs={'location_id': loc_a.location_id})
        self.selenium.get(url)

        for field_name in ['editors_notes', 'element_1_eg_room', 'element_4_eg_city', 'latitude']:
            self.assertEqual(self.selenium.find_element(By.ID, f'id_{field_name}').get_attribute('value'),
                             getattr(loc_a, field_name))

    def test_full_form__POST(self):
        loc_a = fixtures.create_location_a()
        loc_a.save()
        n_res = loc_a.resources.count()
        n_comment = loc_a.comments.count()

        # check before update
        self.assertEqual(n_res, 0)
        self.assertEqual(n_comment, 0)

        # update web page
        url = self.get_url_by_viewname('location:full_form',
                                       kwargs={'location_id': loc_a.location_id})
        self.selenium.get(url)

        # fill resource
        self.fill_formset_by_dict(fixtures.loc_res_dict_a, 'loc_res')

        # fill comment
        self.fill_formset_by_dict(fixtures.loc_comment_dict_a, 'loc_comment')

        self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()

        # assert result after form submit
        loc_a.refresh_from_db()

        # assert resource
        self.assertEqual(loc_a.resources.count(), 1)
        self.assertEqual(loc_a.resources.first().resource_name,
                         fixtures.loc_res_dict_a['resource_name'])

        # assert comment
        self.assertEqual(loc_a.comments.count(), 1)
        self.assertEqual(loc_a.comments.first().comment,
                         fixtures.loc_comment_dict_a['comment'])
