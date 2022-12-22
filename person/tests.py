from selenium.webdriver.common.by import By

import person.fixtures
from core import constant
from core.helper import selenium_utils, model_utils
from person.models import CofkUnionPerson
from siteedit2.utils import test_utils
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form, MultiM2MTester, ResourceM2MTester, \
    CommentM2MTester, CommonSearchTests


class PersonFormTest(EmloSeleniumTestCase):

    def create_full_form_url(self, iperson_id):
        return self.get_url_by_viewname('person:full_form', iperson_id=iperson_id)

    def test_create_person(self):
        self.selenium.get(self.get_url_by_viewname('person:init_form'))

        self.fill_form_by_dict(person.fixtures.person_min_dict_a.items(), )

        new_id = simple_test_create_form(self, CofkUnionPerson)

        pson = CofkUnionPerson.objects.get(iperson_id=new_id)
        self.assertEqual(pson.foaf_name,
                         person.fixtures.person_min_dict_a.get('foaf_name'))

    def test_full_form__GET_simple(self):
        pson_a = test_utils.create_person_by_dict()

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
            ResourceM2MTester(self, pson_a.cofkpersonresourcemap_set, formset_prefix='res'),
            CommentM2MTester(self, pson_a.cofkpersoncommentmap_set, formset_prefix='comment'),
        ])

        url = self.create_full_form_url(pson_a.iperson_id)
        self.selenium.get(url)

        new_further_reading = 'new_further_reading'
        further_reading_ele = self.selenium.find_element(value='id_further_reading')
        selenium_utils.remove_all_text(further_reading_ele)
        further_reading_ele.send_keys(new_further_reading)

        m2m_tester.fill()

        self.click_submit()

        # assert result after form submit
        pson_a.refresh_from_db()

        self.assertEqual(pson_a.further_reading, new_further_reading)

        m2m_tester.assert_after_update()

    def test_recref(self):
        pson_a = test_utils.create_person_by_dict()
        test_utils.create_location_by_dict()

        form_url = self.create_full_form_url(pson_a.iperson_id)
        test_cases = [
            dict(recref_form_name='new_other_loc',
                 target_obj=pson_a,
                 related_manager=pson_a.cofkpersonlocationmap_set,
                 expected_rel_type=constant.REL_TYPE_WAS_IN_LOCATION,
                 form_url=form_url, ),
            dict(recref_form_name='death_place',
                 target_obj=pson_a,
                 related_manager=pson_a.cofkpersonlocationmap_set,
                 expected_rel_type=constant.REL_TYPE_DIED_AT_LOCATION,
                 form_url=form_url, ),
            dict(recref_form_name='new_parent',
                 target_obj=pson_a,
                 related_manager=pson_a.active_relationships,
                 expected_rel_type=constant.REL_TYPE_PARENT_OF,
                 form_url=form_url, ),

            dict(recref_form_name='new_protege',
                 target_obj=pson_a,
                 related_manager=pson_a.active_relationships,
                 expected_rel_type=constant.REL_TYPE_WAS_PATRON_OF,
                 form_url=form_url, ),
        ]
        test_utils.run_recref_test_by_test_cases(self, test_cases)


def prepare_person_records() -> list[CofkUnionPerson]:
    return model_utils.create_multi_records_by_dict_list(CofkUnionPerson, (
        person.fixtures.person_dict_a,
        person.fixtures.person_dict_b,
    ))


class PersonCommonSearchTests(EmloSeleniumTestCase, CommonSearchTests):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_common_search_test(self, 'person:search', prepare_person_records)

    def test_search__search_unique(self):
        def _fill(target_record):
            ele = self.selenium.find_element(By.ID, 'id_iperson_id')
            ele.send_keys(target_record.iperson_id)

        def _check(target_record):
            self.assertEqual(self.find_entry_id_by_table_rows(0),
                             str(target_record.iperson_id))

        self._test_search__search_unique(_fill, _check)
