import re

from selenium.webdriver.common.by import By

from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE
from siteedit2.utils.test_utils import EmloSeleniumTestCase, InputBoxTester, \
    FieldCheckboxTester
from work.models import CofkUnionWork


class WorkFormTests(EmloSeleniumTestCase):

    def test_corr__create(self):
        self.selenium.get(self.get_url_by_viewname('work:corr_form'))

        self.find_element_by_css('#id_author_comment-0-comment').send_keys('xxxxxx')
        input_box_tester = InputBoxTester(self, [
            ('authors_as_marked', 'akdjalksdj')
        ])
        input_box_tester.fill()
        checkbox_tester = FieldCheckboxTester(self, [
            ('authors_inferred', 1),
            ('addressees_uncertain', 1),
        ])
        checkbox_tester.click_checkboxes()

        self.click_submit()

        # find iwork_id from url
        iwork_id = re.findall(r'/work/form/corr/(\d+)', self.selenium.current_url)
        self.assertTrue(iwork_id)
        iwork_id = iwork_id[0]

        # assert work object
        work = CofkUnionWork.objects.filter(iwork_id=iwork_id).first()
        self.assertIsNotNone(work)
        self.assertTrue(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_AUTHOR)
                        .count() > 0)

        input_box_tester.assert_all(work)
        checkbox_tester.assert_all(work)

        # unchanged field
        self.assertEqual(work.authors_uncertain, 0)
        self.assertEqual(work.addressees_inferred, 0)
        self.assertTrue(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_ADDRESSEE)
                        .count() == 0)

    def test_switch_tab_without_save(self):
        self.selenium.get(self.get_url_by_viewname('work:corr_form'))
        self.assertTrue(
            self.selenium.current_url.endswith('/work/form/corr/')
        )
