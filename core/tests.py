from siteedit2.utils.test_utils import EmloSeleniumTestCase


# Create your tests here.

class TestEmloSeleniumTestCase(EmloSeleniumTestCase):

    def test_static_page_exist(self):
        url = self.live_server_url + '/static/core/js/jquery-3.6.0.min.js'
        self.selenium.get(url)
        self.assertGreater(len(self.selenium.page_source), 1000)
