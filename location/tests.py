import re

from selenium.webdriver.common.by import By

from core import fixtures as core_fixtures
from location import fixtures as loc_fixtures
from location.models import CofkUnionLocation
from siteedit2.utils import test_utils
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form


class LocationFormTests(EmloSeleniumTestCase):
    # KTODO test validate fail
    # KTODO test upload images

    def test_create_location(self):
        self.selenium.get(self.get_url_by_viewname('location:init_form'))

        self.fill_form_by_dict(loc_fixtures.location_dict_a.items(),
                               exclude_fields=['location_name'], )

        new_id = simple_test_create_form(self, CofkUnionLocation)

        loc = CofkUnionLocation.objects.get(location_id=new_id)
        self.assertEqual(loc.element_1_eg_room, loc_fixtures.location_dict_a.get('element_1_eg_room'))

    def test_full_form__GET(self):
        loc_a = loc_fixtures.create_location_a()
        loc_a.save()
        url = self.get_url_by_viewname('location:full_form',
                                       kwargs={'location_id': loc_a.location_id})
        test_utils.simple_test_full_form__GET(
            self, loc_a,
            url, ['editors_notes', 'element_1_eg_room', 'element_4_eg_city', 'latitude']
        )

    def test_full_form__POST(self):
        loc_a = loc_fixtures.create_location_a()
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
        self.fill_formset_by_dict(core_fixtures.res_dict_a, 'loc_res')

        # fill comment
        self.fill_formset_by_dict(core_fixtures.comment_dict_a, 'loc_comment')

        self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()

        # assert result after form submit
        loc_a.refresh_from_db()

        # assert resource
        self.assertEqual(loc_a.resources.count(), 1)
        self.assertEqual(loc_a.resources.first().resource_name,
                         core_fixtures.res_dict_a['resource_name'])

        # assert comment
        self.assertEqual(loc_a.comments.count(), 1)
        self.assertEqual(loc_a.comments.first().comment,
                         core_fixtures.comment_dict_a['comment'])


def prepare_loc_records() -> list[CofkUnionLocation]:
    loc_list = [CofkUnionLocation(**loc_dict)
                for loc_dict in (
                    loc_fixtures.location_dict_a,
                    loc_fixtures.location_dict_b,
                )]
    CofkUnionLocation.objects.bulk_create(loc_list)
    return loc_list


class LocationSearchTests(EmloSeleniumTestCase):

    def find_result_elements(self):
        return self.selenium.find_elements(By.CSS_SELECTOR, 'tbody tr.selectable_entry')

    def find_search_btn(self):
        return self.selenium.find_element(By.CSS_SELECTOR, 'button[name=__form_action][value=search]')

    def find_elements_by_css(self, css_selector):
        return self.selenium.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def find_element_by_css(self, css_selector):
        return self.selenium.find_element(by=By.CSS_SELECTOR, value=css_selector)

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
        # prepare data
        loc_list = prepare_loc_records()

        # go to search page
        url = self.get_url_by_viewname('location:search')
        self.selenium.get(url)

        self.assert_search_page(num_row_show=len(loc_list),
                                num_total=len(loc_list))

        target_loc = loc_list[1]

        # search by name
        ele = self.selenium.find_element(By.ID, 'id_location_name')
        ele.send_keys(target_loc.location_name)

        self.find_search_btn().click()

        # only have one record match
        self.assert_search_page(num_row_show=1,
                                num_total=1)

        # check location name in record result
        result_ele = self.find_result_elements()[0]
        location_name = result_ele.find_elements(By.CSS_SELECTOR, 'td')[0].text
        self.assertEqual(location_name, target_loc.location_name)

    def setup_for_layout_test(self, layout_btn_id):
        prepare_loc_records()
        url = self.get_url_by_viewname('location:search')
        self.selenium.get(url)
        self.selenium.find_element(value=layout_btn_id).click()
        self.find_search_btn().click()

    def test_search__table_layout(self):
        self.setup_for_layout_test('display-as-list')
        self.assertIsNotNone(self.find_element_by_css('#search_form table'))

    def test_search__compact_layout(self):
        self.setup_for_layout_test('display-as-grid')
        self.assertIsNotNone(self.find_element_by_css('ol li[class=search-result]'))
