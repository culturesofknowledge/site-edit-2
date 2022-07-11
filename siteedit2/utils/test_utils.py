from typing import Iterable

from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By


class EmloSeleniumTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = 'pycharm-py'

        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-dev-shm-usage")
        cls.selenium = webdriver.Remote(
            command_executor='http://chrome:4444/wd/hub',
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

    def fill_val_by_selector_list(self, selector_list: Iterable[tuple]):
        for selector, val in selector_list:
            ele = self.selenium.find_element(by=By.CSS_SELECTOR, value=selector)
            ele.send_keys(val)
