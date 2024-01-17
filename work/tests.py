import re
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from core import fixtures, constant
from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_COMMENT_DATE, \
    REL_TYPE_COMMENT_DESTINATION, REL_TYPE_COMMENT_ROUTE, REL_TYPE_COMMENT_ORIGIN, REL_TYPE_COMMENT_REFERS_TO, \
    REL_TYPE_CREATED, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_ADDRESSED_TO, \
    REL_TYPE_WAS_SENT_TO, REL_TYPE_IS_RELATED_TO
from core.fixtures import fixture_default_lookup_catalogue, res_dict_a, res_dict_b
from core.helper import test_serv
from core.helper.test_serv import EmloSeleniumTestCase, FieldValTester, CommonSearchTests
from core.models import Iso639LanguageCode, CofkUnionResource, CofkUnionSubject, CofkUnionComment, \
    CofkUnionFavouriteLanguage
from location import fixtures as location_fixtures
from manifestation import fixtures as manif_fixtures
from manifestation.models import CofkUnionManifestation
from person import fixtures as person_fixtures
from work import fixtures as work_fixtures
from work import work_serv
from work.models import CofkUnionWork, CofkUnionLanguageOfWork
from work.recref_adapter import WorkLocRecrefAdapter, WorkResourceRecrefAdapter, WorkCommentRecrefAdapter, \
    WorkPersonRecrefAdapter


def wait_jquery_ready(selenium):
    return selenium.execute_script('return jQuery.active == 0')


class WorkFormTests(EmloSeleniumTestCase):

    def get_id_by_url_pattern(self, re_pattern):
        iwork_id = re.findall(re_pattern, self.selenium.current_url)
        self.assertTrue(iwork_id)
        iwork_id = iwork_id[0]
        return iwork_id

    def test_switch_tab_without_save(self):
        org_size = CofkUnionWork.objects.count()

        def _assert_url_case(url_endswith):
            self.assertTrue(self.selenium.current_url.endswith(url_endswith))

            # should have not CofkUnionWork created after change tab
            self.assertEqual(CofkUnionWork.objects.count(), org_size)

        self.goto_vname('work:corr_form')
        _assert_url_case('/work/form/corr/')

        self.goto_vname('work:dates_form')
        _assert_url_case('/work/form/dates/')

        self.goto_vname('work:places_form')
        _assert_url_case('/work/form/places/')

        self.goto_vname('work:details_form')
        _assert_url_case('/work/form/details/')

    def save_work(self, work: CofkUnionWork):
        work.work_id = work_serv.create_work_id(work.iwork_id)
        work.update_current_user_timestamp('test_user')
        work.save()
        return work

    def test_corr__create(self):
        self.goto_vname('work:corr_form')

        # fill form
        self.find_element_by_css('#id_author_comment-0-comment').send_keys('xxxxxx')
        field_val_tester = FieldValTester(self, [
            ('authors_as_marked', 'akdjalksdj'),
            ('authors_inferred', 1),
            ('addressees_uncertain', 1),
        ])
        field_val_tester.fill()

        self.click_submit()

        # assert work object
        iwork_id = self.get_id_by_url_pattern(r'/work/form/corr/(\d+)')
        work = CofkUnionWork.objects.filter(iwork_id=iwork_id).first()
        self.assertIsNotNone(work)
        self.assertGreater(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_AUTHOR)
                           .count(), 0)
        field_val_tester.assert_all(work)

        # unchanged field
        self.assertEqual(work.authors_uncertain, 0)
        self.assertEqual(work.addressees_inferred, 0)
        self.assertEqual(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_ADDRESSEE)
                         .count(), 0)

    def test_corr__update(self):

        work = CofkUnionWork()
        work.authors_uncertain = 1
        work.authors_as_marked = 'xxxxxx'
        self.save_work(work)

        self.goto_vname('work:corr_form', iwork_id=work.iwork_id)

        authors_as_marked_ele = self.find_element_by_css('#id_authors_as_marked')

        # assert db data have be loaded
        self.assertEqual(
            authors_as_marked_ele.get_attribute('value'),
            work.authors_as_marked,
        )
        self.assertIsNone(self.find_element_by_css('#id_authors_inferred').get_attribute('checked'))
        self.assertIsNotNone(self.find_element_by_css('#id_authors_uncertain').get_attribute('checked'))

        # edit for and submit
        input_authors_as_marked = 'wwwwwww'
        authors_as_marked_ele.clear()
        authors_as_marked_ele.send_keys(input_authors_as_marked)

        self.click_submit()

        # assert db updated
        work.refresh_from_db()
        work.authors_as_marked = input_authors_as_marked

    def test_corr__recref(self):
        test_serv.create_empty_lookup_cat()
        work = test_serv.create_work_by_dict()

        test_serv.create_person_by_dict()
        form_url = self.get_url_by_viewname('work:corr_form', iwork_id=work.iwork_id)
        test_cases = [
            dict(recref_form_name='selected_author_id',
                 target_obj=work,
                 related_manager=work.cofkworkpersonmap_set,
                 expected_rel_type=constant.REL_TYPE_CREATED,
                 form_url=form_url, ),
            dict(recref_form_name='selected_addressee_id',
                 target_obj=work,
                 related_manager=work.cofkworkpersonmap_set,
                 expected_rel_type=constant.REL_TYPE_WAS_ADDRESSED_TO,
                 form_url=form_url, ),
            dict(recref_form_name='new_earlier_letter',
                 target_obj=work,
                 related_manager=work.work_to_set,
                 expected_rel_type=constant.REL_TYPE_WORK_IS_REPLY_TO,
                 form_url=form_url, ),
        ]
        test_serv.run_recref_test_by_test_cases(self, test_cases)

    def test_detes__create(self):
        self.goto_vname('work:dates_form')

        # fill form
        field_val_tester = FieldValTester(self, [
            ('date_of_work_as_marked', 'akdjalksdj'),
            ('date_of_work_std_day', 12),
            ('date_of_work_std_year', 2020),
            ('date_of_work_std_is_range', 1),
            ('date_of_work_uncertain', 1),
            ('date_of_work_std_month', 8),
        ])
        field_val_tester.fill()
        self.find_element_by_css('#id_date_comment-0-comment').send_keys('xxxxxx')

        self.click_submit()

        # assert work object
        iwork_id = self.get_id_by_url_pattern(r'/work/form/dates/(\d+)')
        work = CofkUnionWork.objects.filter(iwork_id=iwork_id).first()
        self.assertIsNotNone(work)
        self.assertGreater(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_DATE)
                           .count(), 0)
        field_val_tester.assert_all(work)

        # unchanged field
        self.assertEqual(work.date_of_work_inferred, 0)
        self.assertEqual(work.date_of_work_approx, 0)

    def test_places__create(self):
        self.goto_vname('work:places_form')
        field_val_tester = FieldValTester(self, [
            ('origin_as_marked', 'akdjalksdj'),
            ('origin_uncertain', 1),
        ])
        field_val_tester.fill()
        self.find_element_by_css('#id_destination_comment-0-comment').send_keys('xxxxxx')
        self.find_element_by_css('#id_route_comment-0-comment').send_keys('xxxxxx')

        self.click_submit()

        # assert work object
        iwork_id = self.get_id_by_url_pattern(r'/work/form/places/(\d+)')
        work = CofkUnionWork.objects.filter(iwork_id=iwork_id).first()
        self.assertIsNotNone(work)
        field_val_tester.assert_all(work)

        # assert comment
        self.assertGreater(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_DESTINATION)
                           .count(), 0)
        self.assertGreater(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_ROUTE)
                           .count(), 0)
        self.assertEqual(work.cofkworkcommentmap_set.count(), 2)

        # unchanged field
        self.assertEqual(work.destination_as_marked, '')
        self.assertEqual(work.origin_inferred, 0)
        self.assertEqual(work.destination_inferred, 0)
        self.assertEqual(work.destination_uncertain, 0)
        self.assertEqual(work.cofkworkcommentmap_set.filter(relationship_type=REL_TYPE_COMMENT_ORIGIN)
                         .count(), 0)

    def prepare_language_data(self):
        lang_list = [Iso639LanguageCode(**lang_dict)
                     for lang_dict in [fixtures.lang_dict_eng, fixtures.lang_dict_ara]]
        for lang in lang_list:
            lang.save()
            CofkUnionFavouriteLanguage(language_code=lang).save()

        return lang_list

    def select_languages(self, input_lang_list):
        self.js_click('.lang_div .sf-select')
        for lang in input_lang_list:
            js = f"""
            let input_ele = document.querySelector('.lang_div .sf-input');
            input_ele.value = '{lang}';
            $(input_ele).trigger('keyup'); 
            input_ele.dispatchEvent(new KeyboardEvent("keydown", {{key: "Enter", bubbles: true}}))
            """
            self.selenium.execute_script(js)

    def test_details__create(self):
        self.prepare_language_data()

        self.goto_vname('work:details_form')

        input_lang_list = {'English', 'Arabic'}
        field_val_tester = FieldValTester(self, [
            ('editors_notes', 'akdjalksdj'),
            ('incipit', 'aaa'),
            ('ps', 'kjs'),
            ('keywords', 'xxxx'),
        ])
        field_val_tester.fill()
        self.find_element_by_css('#id_people_comment-0-comment').send_keys('xxxxxx')

        # select language
        self.select_languages(input_lang_list)

        self.click_submit()

        # assert work object
        iwork_id = self.get_id_by_url_pattern(r'/work/form/details/(\d+)')
        work: CofkUnionWork = CofkUnionWork.objects.filter(iwork_id=iwork_id).first()
        self.assertIsNotNone(work)
        field_val_tester.assert_all(work)
        self.assertIsNotNone(next(work.person_comments, None))
        self.assertEqual(work.language_set.count(), 2)
        self.assertSetEqual(
            {l.language_code.language_name for l in work.language_set.iterator()},
            input_lang_list
        )

        # unchanged field
        self.assertEqual(work.accession_code, '')
        self.assertEqual(work.explicit, '')
        self.assertIsNone(next(work.general_comments, None))

    def test_manif__create(self):
        self.prepare_language_data()

        work = self.save_work(CofkUnionWork())
        input_lang_list = {'English', }

        self.goto_vname('work:manif_init', iwork_id=work.iwork_id)
        iwork_id = self.get_id_by_url_pattern(r'/work/form/manif/(\d+)')
        self.assertEqual(iwork_id and int(iwork_id), work.iwork_id)

        self.selenium.maximize_window()

        field_val_tester = FieldValTester(self, [
            ('manifestation_type', 'E'),
            ('printed_edition_details', 'xkxkx'),
            ('manifestation_creation_date_month', 4),
            ('manifestation_creation_date_approx', 1),
            ('accompaniments', 'asdjask'),
            ('routing_mark_stamp', 'ksksk'),
            ('endorsements', 'zzzz'),
            ('manifestation_is_translation', 1),
        ])
        field_val_tester.fill()

        self.select_languages(input_lang_list)

        self.click_submit()

        # assert work object
        manif_id = re.findall(r'/work/form/manif/(\d+)/([^/#]+)', self.selenium.current_url)
        self.assertTrue(manif_id)
        manif_id = manif_id[0][1]
        manif = CofkUnionManifestation.objects.filter(manifestation_id=manif_id).first()
        self.assertIsNotNone(manif)

        field_val_tester.assert_all(manif)
        self.assertSetEqual(
            {l.language_code.language_name for l in manif.language_set.iterator()},
            input_lang_list
        )

        # unchanged field
        self.assertEqual(manif.manifestation_excipit, '')
        self.assertEqual(manif.manifestation_incipit, '')
        self.assertEqual(manif.non_letter_enclosures, '')
        self.assertEqual(manif.manifestation_creation_date_inferred, 0)


def create_related_obj_by_obj_dict(work, obj, rel_type: str, recref_adapter):
    obj.save()
    recref_adapter(work).upsert_recref(
        rel_type, work, obj
    ).save()


def prepare_works_for_search(core_constant=None):
    fixture_default_lookup_catalogue()
    works = []
    for w in [
        work_fixtures.work_dict_a,
        work_fixtures.work_dict_b,
    ]:
        works.append(work_fixtures.fixture_work_by_dict(w))

    target_work = works[0]
    # recref_serv.upsert_recref()

    #  person relationship
    create_related_obj_by_obj_dict(target_work,
                                   person_fixtures.create_person_obj_by_dict(person_fixtures.person_dict_a),
                                   REL_TYPE_CREATED, WorkPersonRecrefAdapter)
    create_related_obj_by_obj_dict(target_work,
                                   person_fixtures.create_person_obj_by_dict(person_fixtures.person_dict_b),
                                   REL_TYPE_WAS_ADDRESSED_TO, WorkPersonRecrefAdapter)

    # location relationship
    create_related_obj_by_obj_dict(target_work,
                                   location_fixtures.create_location_obj_by_dict(location_fixtures.location_dict_a),
                                   REL_TYPE_WAS_SENT_FROM, WorkLocRecrefAdapter)
    create_related_obj_by_obj_dict(target_work,
                                   location_fixtures.create_location_obj_by_dict(location_fixtures.location_dict_b),
                                   REL_TYPE_WAS_SENT_TO, WorkLocRecrefAdapter)

    manif_a = manif_fixtures.create_manif_obj_by_dict(manif_fixtures.manif_dict_a)
    manif_a.work = target_work
    manif_a.save()

    # resource relationship
    for res_dict in [res_dict_a, res_dict_b]:
        create_related_obj_by_obj_dict(target_work,
                                       CofkUnionResource(**res_dict),
                                       REL_TYPE_IS_RELATED_TO, WorkResourceRecrefAdapter)

    # subject relationship
    subject = CofkUnionSubject(subject_id=19191,
                               subject_desc='Astronomy')
    subject.save()
    target_work.subjects.add(subject)
    target_work.save()

    # comment relationship
    for comment in ['comment a', 'comment b']:
        create_related_obj_by_obj_dict(target_work,
                                       CofkUnionComment(comment=comment),
                                       REL_TYPE_COMMENT_REFERS_TO, WorkCommentRecrefAdapter)

    # language relationship
    lang_en = Iso639LanguageCode(code_639_3='eng',
                                 code_639_1='en',
                                 language_name='English', )
    lang_en.save()
    lang_jp = Iso639LanguageCode(code_639_3='jpn',
                                 code_639_1='jp',
                                 language_name='Japanese', )
    lang_jp.save()

    CofkUnionLanguageOfWork(work=target_work,
                            language_code=lang_en,
                            notes='notes a').save()
    CofkUnionLanguageOfWork(work=target_work,
                            language_code=lang_jp,
                            notes='notes b').save()

    # update queryable work TOBEREMOVE
    # work_serv.clone_queryable_work(target_work, reload=True)

    return works


@dataclass
class ExpandedRow:
    editors_notes: str
    date_for_ordering: str
    author_sender: str
    origin: str
    addressee: str
    destination: str
    uncertainties: str
    images: str
    manifestations: str
    related_resources: str
    subjects: str
    other_details: str
    id: str
    last_edit: str


def assert_table_row(test_case, table_row, expected_data: dict):
    for k, v in expected_data.items():
        test_case.assertEqual(getattr(table_row, k), v)


class WorkSearchTests(EmloSeleniumTestCase, CommonSearchTests):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_common_search_test(self, 'work:search', prepare_works_for_search)

    def test_display_fields_in_list_view(self):
        table_type_id, data_type = 'display-as-list', ExpandedRow
        works = prepare_works_for_search()
        self.goto_search_page()
        self.find_search_btn().click()
        self.find_element_by_css(f'label[for={table_type_id}]').click()
        self.find_search_btn().click()

        for e in self.find_elements_by_css('#hidden_columns > span'):
            e.click()

        table_row_data_dict = dict()

        for row in self.find_elements_by_css('#results_table tr[entry_id]'):
            values = []
            for td in row.find_elements(By.CSS_SELECTOR, 'td'):
                values.append(td.text.strip())

            # row.get_dom_attribute()
            row: WebElement
            obj = data_type(*values)
            obj.id = int(row.get_attribute('entry_id'))
            table_row_data_dict[obj.id] = obj

        target_work = works[0]

        expected_data = dict(
            editors_notes=target_work.editors_notes,
            date_for_ordering='1122-11-22\nAs marked: work_dict_a.date_of_work_as_marked',
            author_sender='person aaaa b. 1921',
            origin='location_name value\n\nAs marked: origin_as_marked value',
            addressee='person bbbb d. 1922',
            destination='location_name value 2',
            uncertainties='',
            images='',
            manifestations='ABC. Postmark: postage_marks a. id_number_or_shelfmark a printed_edition_details a',
            related_resources='Resources:\nresource_name a\nresource_name b',
            subjects='Astronomy',
            other_details='Keywords: keywords value\n\nAbstract: abstract value\n\nLanguages: English (notes a), Japanese (notes b)\n\nNotes: comment a, comment b',
            id=target_work.iwork_id,
        )
        assert_table_row(self, table_row_data_dict[target_work.iwork_id], expected_data)

    def test_search_fields(self):
        """ should have no exception  """

        search_field_values = {
            'description': 'a',
            'date_of_work_as_marked': '1911',
            'date_of_work_std_year': '1911',
            'date_of_work_std_month': '1',
            'date_of_work_std_day': '2',
            'date_of_work_std_from': '1111',
            'date_of_work_std_to': '1112',
            'sender_or_recipient': 'a',
            'origin_or_destination': 'a',
            'creators_searchable': 'a',
            'notes_on_authors': 'a',
            'addressees_searchable': 'a',
            'places_from_searchable': 'a',
            'editors_notes': 'a',
            'places_to_searchable': 'a',
            'flags': 'a',
            'images': 'a',
            'manifestations_searchable': 'a',
            'related_resources': 'a',
            'language_of_work': 'a',
            'abstract': 'a',
            'general_notes': 'a',
            'original_catalogue': 'a',
            'accession_code': 'a',
            'mentioned_searchable': 'a',
            # 'origin_as_marked': 'a',
            'destination_as_marked': 'a',
            'subjects': 'a',
            'keywords': 'a',
            # 'drawer': 'a',
            'iwork_id': 'a',
            'change_timestamp_from': '1111',
            'change_timestamp_to': '1112',
        }

        table_type_id = 'display-as-list'
        works = prepare_works_for_search()
        self.goto_search_page()
        self.find_search_btn().click()
        self.find_element_by_css(f'label[for={table_type_id}]').click()

        for k, v in search_field_values.items():
            self.find_element_by_css('.actionbox button[type=button]').click()
            self.find_element_by_css(f'input[name={k}]').send_keys(v)
            self.find_search_btn().click()
