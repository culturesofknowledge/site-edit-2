import unittest

from django.test import TestCase
from selenium.webdriver.common.by import By

from siteedit2.utils.test_utils import EmloSeleniumTestCase


class WorkFormTests(EmloSeleniumTestCase):

    @unittest.SkipTest
    def test_(self):
        # KTODO
        self.selenium.get(self.get_url_by_viewname('work:corr_form'))

        self.find_element_by_css('#id_authors_as_marked').send_keys('akdjalksdj')

        self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()
