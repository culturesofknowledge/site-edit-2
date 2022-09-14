import re
from typing import Iterable, Type

from django.conf import settings
from django.db.models import Model
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By


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
