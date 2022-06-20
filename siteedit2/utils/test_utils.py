from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities


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
