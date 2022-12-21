import logging
import re
from typing import Iterable, Type, Any

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import models
from django.db.models import Model
from django.urls import reverse
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

import core.fixtures
import location.fixtures
import person.fixtures
from core.helper import model_utils
from core.helper.view_utils import BasicSearchView
from core.models import CofkLookupCatalogue
from location.models import CofkUnionLocation
from login.models import CofkUser
from person.models import CofkUnionPerson
from work.fixtures import work_dict_a
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


class EmloSeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = settings.TEST_WEB_HOST

        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-dev-shm-usage")
        cls.selenium = webdriver.Remote(
            command_executor=f'http://{settings.SELENIUM_HOST_PORT}/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options,
        )
        cls.selenium.maximize_window()  # avoid something is not clickable
        cls.selenium.implicitly_wait(10)

        cls.login_user = CofkUser()
        cls.login_user.username = 'test_user_a'
        cls.login_user.raw_password = 'pass'
        cls.login_user.set_password(cls.login_user.raw_password)

    def setUp(self) -> None:
        """ Developer can change login_user by overwrite setUpClass
        setUp will no login user if login_user is None
        """
        if self.login_user is not None:
            self.login_user.save()
            self.goto_vname('login:gate')
            self.find_element_by_css('input[name=username]').send_keys(self.login_user.username)
            self.find_element_by_css('input[name=password]').send_keys(self.login_user.raw_password)
            self.find_element_by_css('button').click()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def get_url_by_viewname(self, viewname, *args, **kwargs):
        return self.live_server_url + reverse(viewname, args=args, kwargs=kwargs)

    def fill_form_by_dict(self,
                          model_dict: dict,
                          exclude_fields: Iterable[str] = None):
        if exclude_fields is not None and (exclude_fields := set(exclude_fields)):
            model_dict = ((k, v) for k, v in model_dict if k not in exclude_fields)
        self.fill_val_by_selector_list((f'#id_{k}', v) for k, v in model_dict)

    def fill_val_by_selector_list(self, selector_list: Iterable[tuple]):
        for selector, val in selector_list:
            ele = self.selenium.find_element(by=By.CSS_SELECTOR, value=selector)
            ele.send_keys(val)

    def fill_formset_by_dict(self, data: dict, formset_prefix, form_idx=0):
        self.fill_val_by_selector_list((f'#id_{formset_prefix}-{form_idx}-{k}', v)
                                       for k, v in data.items())

    def find_elements_by_css(self, css_selector):
        return self.selenium.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def find_element_by_css(self, css_selector):
        return self.selenium.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def goto_vname(self, vname, *args, **kwargs):
        self.selenium.get(self.get_url_by_viewname(vname, *args, **kwargs))

    def click_submit(self):
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type=submit].sticky-btn').click()

    def js_click(self, selector):
        script = f"document.querySelector('{selector}').click(); "
        self.selenium.execute_script(script)

    def switch_to_new_window_on_completed(self):
        return SwitchToNewWindow(self.selenium)


def get_selected_radio_val(elements):
    for ele in elements:
        if ele.is_selected():
            return ele.get_attribute('value')
    return None


def simple_test_full_form__GET(selenium_test: EmloSeleniumTestCase,
                               model: Model,
                               full_form_url: str,
                               check_fields: Iterable[str]):
    # load full form
    selenium_test.selenium.get(full_form_url)

    for field_name in check_fields:
        model_val = getattr(model, field_name)
        elements = selenium_test.selenium.find_elements(By.CSS_SELECTOR, f'[name={field_name}]')
        if len(elements) == 1:
            selenium_test.assertEqual(elements[0].get_attribute('value'), model_val)
        elif len(elements) > 1:
            ele_type = elements[0].get_attribute('type')
            if ele_type == 'radio':
                selected_val = get_selected_radio_val(elements)
                selenium_test.assertEqual(selected_val, model_val)
            else:
                raise NotImplementedError(f'unknown type [{ele_type}]')
        else:
            raise Exception(f'field not found -- {field_name}')


def simple_test_create_form(selenium_test: EmloSeleniumTestCase,
                            model_class: Type[Model]):
    org_size = model_class.objects.count()

    submit_btn = selenium_test.selenium.find_element(By.CSS_SELECTOR, '[type=submit]')
    submit_btn.click()

    # check new should be created in db
    selenium_test.assertGreater(model_class.objects.count(), org_size)

    new_id = re.findall(r'.+/(\d+)', selenium_test.selenium.current_url)[0]
    new_id = int(new_id)
    return new_id


class SimpleM2MTester:
    def __init__(self,
                 selenium_test: EmloSeleniumTestCase,
                 related_manager,
                 formset_prefix: str,
                 model_dict: dict, ):
        self.selenium_test = selenium_test
        self.related_manager = related_manager
        self.model_dict = model_dict
        self.formset_prefix = formset_prefix
        self.org_size = self.related_manager.count()

    def fill(self):
        """Step 1: fill form"""
        self.selenium_test.fill_formset_by_dict(self.model_dict, self.formset_prefix)

    def assert_after_update(self):
        """Step 2: assert after update"""

        # related_manager should be refreshed by model.refresh_from_db
        self.selenium_test.assertGreater(self.related_manager.count(), self.org_size)
        self.assert_fn()

    def assert_fn(self):
        raise NotImplementedError()


class ResourceM2MTester(SimpleM2MTester):

    def __init__(self, selenium_test: EmloSeleniumTestCase, related_manager,
                 formset_prefix: str = 'res',
                 model_dict: dict = core.fixtures.res_dict_a,
                 ):
        super().__init__(selenium_test, related_manager, formset_prefix, model_dict)

    def assert_fn(self):
        self.selenium_test.assertEqual(self.related_manager.last().resource.resource_name,
                                       self.model_dict['resource_name'])


class CommentM2MTester(SimpleM2MTester):

    def __init__(self, selenium_test: EmloSeleniumTestCase, related_manager,
                 formset_prefix: str = 'comment',
                 model_dict: dict = core.fixtures.comment_dict_a, ):
        super().__init__(selenium_test, related_manager, formset_prefix, model_dict)

    def assert_fn(self):
        self.selenium_test.assertEqual(self.related_manager.last().comment.comment,
                                       self.model_dict['comment'])


class MultiM2MTester:
    def __init__(self, m2m_tester_list):
        self.m2m_tester_list = m2m_tester_list

    def fill(self):
        for tester in self.m2m_tester_list:
            tester.fill()

    def assert_after_update(self):
        for tester in self.m2m_tester_list:
            tester.assert_after_update()


class CommonSearchTests:
    LAYOUT_VAL_TABLE = 'display-as-list'
    LAYOUT_VAL_COMPACT = 'display-as-grid'

    def setup_common_search_test(self, test_case: EmloSeleniumTestCase,
                                 search_vname,
                                 prepare_records):
        self.test_case = test_case
        self.search_vname = search_vname
        self.prepare_records = prepare_records

    def switch_layout(self, layout_val):
        # assume selenium already in search page
        self.test_case.js_click(f'#{layout_val}')

    def goto_search_page(self):
        self.test_case.goto_vname(self.search_vname)

    def find_search_btn(self):
        return self.test_case.selenium.find_element(By.CSS_SELECTOR, 'button.save[type=submit]')

    def find_table_rows(self):
        return self.test_case.selenium.find_elements(By.CSS_SELECTOR, 'tbody tr.selectable_entry')

    def find_table_col_element(self, row_idx: int = 0, col_idx: int = 0):
        result_ele = self.find_table_rows()[row_idx]
        return result_ele.find_elements(By.CSS_SELECTOR, 'td')[col_idx]

    def setup_for_layout_test(self, layout_val):
        self.prepare_records()
        self.goto_search_page()
        self.switch_layout(layout_val)

    def test_search__GET(self):
        records = self.prepare_records()

        self.goto_search_page()

        self.assert_search_page(num_row_show=min(len(records), BasicSearchView.paginate_by),
                                num_total=len(records))

    def test_search__table_layout(self):
        self.setup_for_layout_test(self.LAYOUT_VAL_TABLE)
        self.test_case.assertIsNotNone(self.test_case.find_element_by_css('#search_form table'))

    def test_search__compact_layout(self):
        self.setup_for_layout_test(self.LAYOUT_VAL_COMPACT)
        self.test_case.assertIsNotNone(self.test_case.find_element_by_css('ol li[class=search-result]'))

    def _test_search__search_unique(self, fill_field_fn, assert_table_result_fn):
        # prepare data
        records = self.prepare_records()

        # go to search page
        self.goto_search_page()

        target_rec = records[0]

        # search by name
        fill_field_fn(target_rec)

        self.find_search_btn().click()

        # only have one record match
        self.assert_search_page(num_row_show=1,
                                num_total=1)

        # check value in record result
        assert_table_result_fn(target_rec)

    def assert_search_page(self, num_row_show, num_total):
        self.test_case.assertEqual(len(self.find_table_rows()), num_row_show, )

        size_titles = (e.text for e in self.test_case.selenium.find_elements(By.CSS_SELECTOR, 'h2'))
        size_titles = (re.findall(r'(\d+) .+? found', t) for t in size_titles)
        size_titles = (s for s in size_titles if s)
        size_titles = list(size_titles)
        self.test_case.assertEqual(len(size_titles), 1)
        self.test_case.assertEqual(size_titles[0][0], f'{num_total}')


class FieldValTester:
    def __init__(self,
                 test_case: EmloSeleniumTestCase,
                 field_values: list[tuple[str, Any]]):
        self.test_case = test_case
        self.field_values = field_values

    def get_element_val_list(self):
        for field_name, val in self.field_values:
            ele = self.test_case.find_element_by_css(f'#id_{field_name}')
            yield ele, val

    def fill(self):
        for ele, val in self.get_element_val_list():
            log.debug(f'fill: {ele.get_attribute("id")}')
            ele_type = ele.get_attribute('type')
            if ele_type == 'checkbox':
                if ele.is_displayed():
                    ele.click()
                else:
                    self.test_case.js_click(f'label[for={ele.get_attribute("id")}]')

            elif ele_type == 'text' or ele.tag_name == 'textarea':
                ele.send_keys(val)
            elif ele.tag_name == 'select':
                Select(ele).select_by_value(str(val))
            else:
                log.warning(f'unexpected input element [{ele.tag_name}][{ele_type}]')
                ele.send_keys(val)

    def assert_all(self, model: models.Model):
        for field_name, expected_val in self.field_values:
            with self.test_case.subTest(field_name=field_name):
                self.test_case.assertEqual(getattr(model, field_name), expected_val)


def create_work_by_dict(work_dict: dict = None, work_id=None) -> CofkUnionWork:
    work_dict = dict(work_dict or work_dict_a)
    if work_id:
        work_dict['work_id'] = work_id
    work = create_model_instance(CofkUnionWork, instance_dict=work_dict)
    return work


def create_person_by_dict(pson_dict: dict = None) -> CofkUnionPerson:
    return create_model_instance(CofkUnionPerson,
                                 instance_dict=pson_dict or person.fixtures.person_dict_a)


def create_location_by_dict(loc_dict: dict = None) -> CofkUnionLocation:
    return create_model_instance(CofkUnionLocation,
                                 instance_dict=loc_dict or location.fixtures.location_dict_a)


def create_model_instance(model_class: Type[model_utils.ModelLike],
                          instance_dict: dict) -> model_utils.ModelLike:
    obj = model_class(**instance_dict)
    obj.save()
    return obj


class SwitchToNewWindow:
    def __init__(self, driver):
        self.driver = driver
        self.window_handlers = set()

    def __enter__(self):
        self.window_handlers = set(self.driver.window_handles)

    def __exit__(self, exc_type, exc_val, exc_tb):
        new_win_set = set(self.driver.window_handles) - self.window_handlers
        if not new_win_set:
            raise RuntimeError(f'No new windows found [{self.driver.window_handles}] ')
        self.driver.switch_to.window(list(new_win_set)[0])


def run_recref_test(test_case: EmloSeleniumTestCase, recref_form_name,
                    target_obj, related_manager, expected_rel_type, form_url):
    n_org_recref = related_manager.count()
    org_id_list = {i.pk for i in related_manager.all()}

    test_case.selenium.get(form_url)

    # select record
    try:
        _selector = f'#id_{recref_form_name}-target_id_select_btn'
        test_case.find_element_by_css(_selector)
    except NoSuchElementException:
        _selector = f'#id_{recref_form_name}_select_btn'
    with test_case.switch_to_new_window_on_completed():
        test_case.js_click(_selector)
    test_case.find_element_by_css('.selectable_entry').click()
    test_case.find_element_by_css('#ok_btn').click()
    test_case.selenium.switch_to.window(test_case.selenium.window_handles[0])

    # check item selected
    try:
        _selector = f'#id_{recref_form_name}-target_id'
        test_case.find_element_by_css(_selector)
    except NoSuchElementException:
        _selector = f'#id_{recref_form_name}'
    selected_id = test_case.find_element_by_css(_selector).get_attribute('value')
    test_case.assertTrue(selected_id)

    # submit
    test_case.click_submit()
    target_obj.refresh_from_db()

    #  assert
    test_case.assertEqual(related_manager.count(),
                          n_org_recref + 1)
    new_recref = related_manager.exclude(pk__in=org_id_list).first()
    test_case.assertIsNotNone(new_recref)
    test_case.assertEqual(new_recref.relationship_type, expected_rel_type)


def run_recref_test_by_test_cases(emlo_test: EmloSeleniumTestCase, test_cases: Iterable[dict]):
    for test_case in test_cases:
        with emlo_test.subTest(recref=test_case['recref_form_name']):
            run_recref_test(emlo_test, **test_case)


def create_empty_lookup_cat() -> CofkLookupCatalogue:
    cat = CofkLookupCatalogue(
        catalogue_code='',
        catalogue_name='empty cat',
        is_in_union=1,
        publish_status=1,
    )
    cat.save()
    return cat
