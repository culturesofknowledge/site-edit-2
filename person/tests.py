from selenium.webdriver.common.by import By

import person.fixtures
from core.helper import selenium_utils
from person.models import CofkUnionPerson
from siteedit2.utils import test_utils
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form, MultiM2MTester, ResourceM2MTester, \
    CommentM2MTester


class PersonInitFormTest(EmloSeleniumTestCase):

    def create_full_form_url(self, iperson_id):
        return self.get_url_by_viewname(
            'person:full_form', kwargs={'iperson_id': iperson_id})

    def test_create_person(self):
        self.selenium.get(self.get_url_by_viewname('person:init_form'))

        self.fill_form_by_dict(person.fixtures.person_min_dict_a.items(), )

        new_id = simple_test_create_form(self, CofkUnionPerson)

        pson = CofkUnionPerson.objects.get(iperson_id=new_id)
        self.assertEqual(pson.foaf_name,
                         person.fixtures.person_min_dict_a.get('foaf_name'))

    def test_full_form__GET_simple(self):
        pson_a = CofkUnionPerson(**person.fixtures.person_dict_a)
        pson_a.save()
        url = self.create_full_form_url(pson_a.iperson_id)
        test_utils.simple_test_full_form__GET(
            self, pson_a,
            url, [
                'foaf_name', 'skos_altlabel', 'person_aliases',
                'further_reading', 'editors_notes',
                'gender',
            ]
        )

    def test_full_form__POST_simple(self):
        pson_a = CofkUnionPerson(**person.fixtures.person_dict_a)
        pson_a.save()

        m2m_tester = MultiM2MTester(m2m_tester_list=[
            ResourceM2MTester(self, pson_a.resources, formset_prefix='res'),
            CommentM2MTester(self, pson_a.comments, formset_prefix='comment'),
        ])

        url = self.create_full_form_url(pson_a.iperson_id)
        self.selenium.get(url)

        new_further_reading = 'new_further_reading'
        further_reading_ele = self.selenium.find_element(value='id_further_reading')
        selenium_utils.remove_all_text(further_reading_ele)
        further_reading_ele.send_keys(new_further_reading)

        m2m_tester.fill()

        self.selenium.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()

        # assert result after form submit
        pson_a.refresh_from_db()

        self.assertEqual(pson_a.further_reading, new_further_reading)

        m2m_tester.assert_after_update()
