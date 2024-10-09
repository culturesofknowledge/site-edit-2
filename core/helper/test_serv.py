import logging
import re
from typing import Iterable, Type, Any

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import models
from django.db.models import Model, Lookup, Value
from django.test import TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

import core.fixtures
import location.fixtures
import person.fixtures
from core.constant import REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_IS_RELATED_TO
from core.helper import model_serv, recref_serv, webdriver_actions
from core.helper.model_serv import ModelLike
from core.helper.recref_serv import RecrefLike
from core.helper.view_serv import BasicSearchView
from core.models import CofkLookupCatalogue, CofkUnionComment, CofkUnionResource
from location.models import CofkUnionLocation
from login.fixtures import create_test_user__a
from person.models import CofkUnionPerson
from work.fixtures import work_dict_a
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


class EmloSeleniumTestCase(StaticLiveServerTestCase):

    @classmethod
    def _get_selenium_driver(cls):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--start-maximized')  # maximize browser window
        if settings.SELENIUM_CHROME_LOCAL_DRIVER:
            # run selenium with your local browser
            if settings.SELENIUM_CHROME_HEADLESS:
                options.add_argument('--headless')
            browser_driver = webdriver.Chrome(options=options)
        else:
            # run selenium with docker remote browser
            options.add_argument("no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            browser_driver = webdriver.Remote(
                command_executor=f'http://{settings.SELENIUM_HOST_PORT}/wd/hub',
                options=options,
            )

        return browser_driver

    @classmethod
    def setUpClass(cls):
        cls.host = settings.TEST_WEB_HOST

        super().setUpClass()
        cls.selenium = cls._get_selenium_driver()
        cls.selenium.maximize_window()  # avoid something is not clickable
        cls.selenium.implicitly_wait(10)

        cls.login_user = create_test_user__a()

    def setUp(self) -> None:
        """ Developer can change login_user by overwrite setUpClass
        setUp will no login user if login_user is None
        """
        if self.login_user is not None:
            self.login_user.save()
            self.goto_vname('login:gate')
            webdriver_actions.login(self.selenium, self.login_user.username, self.login_user.raw_password)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def get_url_by_viewname(self, viewname, *args, **kwargs):
        return self.get_url_by_path(reverse(viewname, args=args, kwargs=kwargs))

    def get_url_by_path(self, path):
        return self.live_server_url + path

    def fill_form_by_dict(self,
                          model_dict: dict,
                          exclude_fields: Iterable[str] = None):
        webdriver_actions.fill_form_by_dict(self.selenium, model_dict, exclude_fields)

    def fill_val_by_selector_list(self, selector_list: Iterable[tuple]):
        webdriver_actions.fill_val_by_selector_list(self.selenium, selector_list)

    def fill_formset_by_dict(self, data: dict, formset_prefix, form_idx=0):
        webdriver_actions.fill_formset_by_dict(self.selenium, data, formset_prefix, form_idx)

    def find_elements_by_css(self, css_selector) -> Iterable[WebElement]:
        return webdriver_actions.find_elements_by_css(self.selenium, css_selector)

    def find_element_by_css(self, css_selector) -> WebElement:
        return webdriver_actions.find_element_by_css(self.selenium, css_selector)

    def goto_vname(self, vname, *args, **kwargs):
        self.selenium.get(self.get_url_by_viewname(vname, *args, **kwargs))

    def goto_path(self, path):
        self.selenium.get(self.get_url_by_path(path))

    def click_submit(self):
        webdriver_actions.click_submit(self.selenium)

    def js_click(self, selector):
        webdriver_actions.js_click(self.selenium, selector)

    def switch_to_new_window_on_completed(self):
        return webdriver_actions.switch_to_new_window(self.selenium)


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


def find_search_btn(selenium):
    return selenium.find_element(By.CSS_SELECTOR, 'button.save[type=submit]')


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
        return find_search_btn(self.test_case.selenium)

    def find_table_rows(self):
        return self.test_case.selenium.find_elements(By.CSS_SELECTOR, 'tbody tr.selectable_entry')

    def find_table_col_element(self, row_idx: int = 0, col_idx: int = 0):
        result_ele = self.find_table_rows()[row_idx]
        return result_ele.find_elements(By.CSS_SELECTOR, 'td')[col_idx]

    def find_entry_id_by_table_rows(self, row_idx):
        row_ele = self.test_case.selenium.find_elements(By.CSS_SELECTOR, 'tbody tr.selectable_entry')[row_idx]
        return row_ele.get_attribute('entry_id')

    def test_search__GET(self):
        records = self.prepare_records()

        self.goto_search_page()

        self.find_search_btn().click()

        self.assert_search_page(num_row_show=min(len(records), BasicSearchView.paginate_by),
                                num_total=len(records))

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
        self.assert_search_page(num_row_show=1, num_total=1)

        # check value in record result
        assert_table_result_fn(target_rec)

    def assert_search_page(self, num_row_show, num_total):
        self.test_case.assertEqual(len(self.find_table_rows()), num_row_show, )

        size_titles = (e.text for e in self.test_case.selenium.find_elements(By.CSS_SELECTOR, 'h2'))
        size_titles = (re.findall(r'out of ([\d,]+)', t) for t in size_titles)
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


def create_model_instance(model_class: Type[model_serv.ModelLike],
                          instance_dict: dict) -> model_serv.ModelLike:
    obj = model_class(**instance_dict)
    obj.save()
    return obj


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


def create_recref_list(parent, models, rel_type):
    recref_list = []
    for model in models:
        model.save()
        recref = recref_serv.find_bounded_data_by_pair_model(parent, model).fill_recref(model, parent)
        recref.relationship_type = rel_type
        recref.save()
        recref_list.append(recref)
    return recref_list


def add_comments_by_msgs(msgs: Iterable[str], parent) -> list[RecrefLike]:

    models = (CofkUnionComment(comment=comment_msg) for comment_msg in msgs)
    recref_list = create_recref_list(parent, models, REL_TYPE_COMMENT_REFERS_TO)
    return recref_list


def add_resources_by_msgs(msgs: Iterable[str], parent) -> list[RecrefLike]:
    models = (CofkUnionResource(resource_name=msg, resource_url=msg) for msg in msgs)
    recref_list = create_recref_list(parent, models, REL_TYPE_IS_RELATED_TO)
    return recref_list


def cnt_recref(recref_class, instance: ModelLike):
    recref_list = recref_serv.find_recref_list(recref_class, instance)
    return len(list(recref_list))


class LoginTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login_user = create_test_user__a()

    def setUp(self) -> None:
        super().setUp()
        self.client.post(reverse('login:gate'), data={
            'username': self.login_user.username,
            'password': self.login_user.raw_password,
        }, follow=True)


def assert_lookup(lookup: Lookup, field_name, value, lookup_type: Type[Lookup]):
    assert lookup.lhs.target.column == field_name
    actual_value = lookup.rhs.value if isinstance(lookup.rhs, Value) else lookup.rhs
    assert actual_value == value
    assert isinstance(lookup, lookup_type)
