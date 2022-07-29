import re

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


class LocationSearchTests(EmloSeleniumTestCase):

    def find_result_elements(self):
        return self.selenium.find_elements(By.CSS_SELECTOR, 'li.search-result')

    def assert_search_page(self, num_row_show, num_total):
        # assert
        self.assertEqual(len(self.find_result_elements()), num_row_show, )

        size_titles = (e.text for e in self.selenium.find_elements(By.CSS_SELECTOR, 'h2'))
        size_titles = (re.findall(r'(\d+) Locations found', t) for t in size_titles)
        size_titles = (s for s in size_titles if s)
        size_titles = list(size_titles)
        self.assertEqual(len(size_titles), 1)
        self.assertEqual(size_titles[0][0], f'{num_total}')

    def test_search_page(self):
        #  prepare data
        loc_list = [CofkUnionLocation(**loc_dict)
                    for loc_dict in (fixtures.location_dict_a, fixtures.location_dict_b,)]
        CofkUnionLocation.objects.bulk_create(loc_list)

        # go to search page
        url = self.get_url_by_viewname('location:search')
        self.selenium.get(url)

        self.assert_search_page(len(loc_list), len(loc_list))

        target_loc = loc_list[1]

        # search by name
        ele = self.selenium.find_element(By.ID, 'id_location_name')
        ele.send_keys(target_loc.location_name)

        self.selenium.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()

        # only have one record match
        self.assert_search_page(1, 1)

        # check location name in record result
        result_ele = self.find_result_elements()[0]
        location_name = result_ele.find_element(By.CSS_SELECTOR, 'div h3 a[href]').text
        self.assertEqual(location_name, target_loc.location_name)
