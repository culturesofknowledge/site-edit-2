import re
from typing import Iterable, Type

from django.conf import settings
from django.db.models import Model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By

import core.fixtures


class EmloSeleniumTestCase(LiveServerTestCase):
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
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def get_url_by_viewname(self, viewname, **kwargs):
        return self.live_server_url + reverse(viewname, **kwargs)

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

    submit_btn = selenium_test.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]')
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
        self.selenium_test.assertEqual(self.related_manager.last().resource_name,
                                       self.model_dict['resource_name'])


class CommentM2MTester(SimpleM2MTester):

    def __init__(self, selenium_test: EmloSeleniumTestCase, related_manager,
                 formset_prefix: str = 'comment',
                 model_dict: dict = core.fixtures.comment_dict_a, ):
        super().__init__(selenium_test, related_manager, formset_prefix, model_dict)

    def assert_fn(self):
        self.selenium_test.assertEqual(self.related_manager.last().comment,
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
