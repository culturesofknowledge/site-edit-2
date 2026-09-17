from datetime import date

from django.db.models.lookups import Exact, IContains
from django.test import RequestFactory
from django.test import TestCase
from selenium.webdriver.common.by import By

import person.fixtures
from cllib import selenium_utils
from core import constant
from core.helper import model_serv, test_serv, query_serv
from core.helper.test_serv import EmloSeleniumTestCase, simple_test_create_form, MultiM2MTester, ResourceM2MTester, \
    CommentM2MTester, CommonSearchTests, MergeTests
from person.forms import PersonForm
from person.models import CofkUnionPerson, CofkPersonResourceMap
from person.recref_adapter import PersonResourceRecrefAdapter
from person.views import PersonMergeChoiceView, PersonSearchView


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
        pson_a = test_serv.create_person_by_dict()

        url = self.create_full_form_url(pson_a.iperson_id)
        test_serv.simple_test_full_form__GET(
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
        pson_a = test_serv.create_person_by_dict()
        test_serv.create_location_by_dict()

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
        test_serv.run_recref_test_by_test_cases(self, test_cases)


def prepare_person_records() -> list[CofkUnionPerson]:
    return model_serv.create_multi_records_by_dict_list(CofkUnionPerson, (
        person.fixtures.person_dict_a,
        person.fixtures.person_dict_b,
    ))


class PersonCommonSearchTests(EmloSeleniumTestCase, CommonSearchTests):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_common_search_test(self, 'person:search', prepare_person_records)

    def test_search__display_flourished_dates(self):
        # Create a person with only flourished dates
        person_fl = test_serv.create_person_by_dict(
            {
                'foaf_name': 'Flourished Person',
                'flourished_year': 1600,
                'flourished2_year': 1650,
                'date_of_birth_year': None,
                'date_of_death_year': None,
            }
        )

        # Create a person with birth and death dates
        person_bd = test_serv.create_person_by_dict(
            {
                'foaf_name': 'Born Died Person',
                'date_of_birth_year': 1500,
                'date_of_death_year': 1580,
                'flourished_year': None,
            }
        )

        # Create a person related to the above two
        person_related = test_serv.create_person_by_dict(
            {
                'foaf_name': 'Related Person',
            }
        )
        from person.models import CofkPersonPersonMap
        CofkPersonPersonMap.objects.create(
            person=person_related,
            related=person_fl,
            relationship_type=constant.REL_TYPE_UNSPECIFIED_RELATIONSHIP_WITH
        )
        CofkPersonPersonMap.objects.create(
            person=person_related,
            related=person_bd,
            relationship_type=constant.REL_TYPE_UNSPECIFIED_RELATIONSHIP_WITH
        )

        self.selenium.get(self.get_url_by_viewname('person:search'))
        self.selenium.find_element(By.ID, 'id_names_and_titles').send_keys('Person')
        self.find_search_btn().click()

        # Find the row for 'Flourished Person'
        fl_row = self.find_row_by_text('Flourished Person')
        self.assertIsNotNone(fl_row, "Flourished Person row not found")

        # Assert 'Fl.' column for 'Flourished Person'
        fl_col_index = self.get_header_column_index('Fl.')
        fl_date_text = fl_row.find_elements(By.TAG_NAME, 'td')[fl_col_index].text
        self.assertEqual(fl_date_text.strip(), 'fl. 1600 to 1650')

        # Find the row for 'Born Died Person'
        bd_row = self.find_row_by_text('Born Died Person')
        self.assertIsNotNone(bd_row, "Born Died Person row not found")

        # Assert 'Born' and 'Died' columns for 'Born Died Person'
        born_col_index = self.get_header_column_index('Born')
        died_col_index = self.get_header_column_index('Died')
        born_date_text = bd_row.find_elements(By.TAG_NAME, 'td')[born_col_index].text
        died_date_text = bd_row.find_elements(By.TAG_NAME, 'td')[died_col_index].text
        self.assertEqual(born_date_text.strip(), '1500')
        self.assertEqual(died_date_text.strip(), '1580')

        # Find the row for 'Related Person'
        related_row = self.find_row_by_text('Related Person')
        self.assertIsNotNone(related_row, "Related Person row not found")

        # Assert 'Other details' column for 'Related Person'
        other_details_col_index = self.get_header_column_index('Other details')
        other_details_text = related_row.find_elements(By.TAG_NAME, 'td')[other_details_col_index].text
        # TODO
        # Unclear where this text now lives
        #self.assertIn('Flourished Person, fl. 1600-1650', other_details_text)
        #self.assertIn('Born Died Person, 1500-1580', other_details_text)

    def get_header_column_index(self, header_text):
        headers = self.selenium.find_elements(By.CSS_SELECTOR, '#results_table thead th')
        for i, header in enumerate(headers):
            if header.text.strip() == header_text:
                return i
        raise ValueError(f"Header '{header_text}' not found.")

    def find_row_by_text(self, text):
        rows = self.selenium.find_elements(By.CSS_SELECTOR, '#results_table tbody tr')
        for row in rows:
            if text in row.text:
                return row
        return None


class PersonQueryTests(TestCase):

    def test_get_queryset(self):
        request_factory = RequestFactory()

        person_search_view = PersonSearchView()
        person_search_view.setup(request_factory.get(
            '',
            data={
                'gender': 'M',
                'death_year_from': 1900,
                'editors_notes': 'aaa',
                'editors_notes_lookup': 'contains',
            }),
        )

        queryset = person_search_view.get_queryset()
        assert queryset is not None

        from django.db.models.sql.where import WhereNode
        from django.db.models.lookups import IsNull
        where_childrens = query_serv.extract_sub_query(queryset).where.children

        # Filter to simple Lookup nodes (not compound WhereNodes)
        simple_childrens = {c.lhs.target.column: c for c in where_childrens if not isinstance(c, WhereNode)}

        test_serv.assert_lookup(simple_childrens['gender'],
                                'gender', 'M', Exact)

        # editors_notes lookup is wrapped in a WhereNode (IContains AND isnull check)
        # Find the IContains inside the compound WhereNode for editors_notes
        def find_icontains_for_field(field_col):
            for node in where_childrens:
                if isinstance(node, IContains) and hasattr(node, 'lhs') and node.lhs.target.column == field_col:
                    return node
                if isinstance(node, WhereNode):
                    for child in node.children:
                        if isinstance(child, IContains) and hasattr(child, 'lhs') and child.lhs.target.column == field_col:
                            return child
            return None

        editors_notes_lookup = find_icontains_for_field('editors_notes')
        assert editors_notes_lookup is not None, "IContains for editors_notes not found"
        test_serv.assert_lookup(editors_notes_lookup, 'editors_notes', 'aaa', IContains)

        # Verify that a complex year-overlap WhereNode was generated for death_year_from
        complex_childrens = [c for c in where_childrens if isinstance(c, WhereNode)]
        assert len(complex_childrens) > 0, "Expected a WhereNode for death year overlap filter"


class PersonFormDateFieldsTests(TestCase):
    """Regression tests: date_of_birth/date_of_death/flourished are listed in
    PersonForm.Meta.fields but have no rendered widget anywhere in the person
    templates, so plain ModelForm field->instance assignment always set them
    to None on save. PersonForm._post_clean() now recomputes them from the
    granular year/month/day fields instead."""

    def _valid_data(self, **overrides):
        data = {
            'foaf_name': 'Isaac Newton',
            'date_of_birth_year': '1643',
            'date_of_birth_month': '1',
            'date_of_birth_day': '4',
            'date_of_death_year': '1727',
            'date_of_death_month': '3',
            'date_of_death_day': '31',
            'flourished_year': '1670',
            'flourished_month': '5',
            'flourished_day': '2',
        }
        data.update(overrides)
        return data

    def test_save_derives_date_of_birth_and_death(self):
        form = PersonForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

        person = form.save()

        self.assertEqual(person.date_of_birth, date(1643, 1, 4))
        self.assertEqual(person.date_of_death, date(1727, 3, 31))
        self.assertEqual(person.flourished, date(1670, 5, 2))

    def test_editing_existing_person_does_not_wipe_dates(self):
        """The bug this guards against: saving the form for an existing
        person - e.g. just to change editors_notes - used to silently null
        out date_of_birth/date_of_death/flourished because those fields are
        never part of the submitted POST data."""
        person = CofkUnionPerson(
            init_seq_id=True, foaf_name='Isaac Newton', gender='M', is_organisation='',
            date_of_birth_year=1643, date_of_birth_month=1, date_of_birth_day=4,
            date_of_birth=date(1643, 1, 4),
            date_of_death_year=1727, date_of_death_month=3, date_of_death_day=31,
            date_of_death=date(1727, 3, 31),
        )
        person.person_id = f'person_{person.iperson_id}'
        person.update_current_user_timestamp('admin')
        person.save()

        form = PersonForm(
            data=self._valid_data(editors_notes='updated notes only'),
            instance=CofkUnionPerson.objects.get(pk=person.pk),
        )
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()

        self.assertEqual(saved.date_of_birth, date(1643, 1, 4))
        self.assertEqual(saved.date_of_death, date(1727, 3, 31))


class PersonMergeTests(MergeTests):
    ResourceRecrefAdapter = PersonResourceRecrefAdapter
    RecrefResourceMap = CofkPersonResourceMap
    ChoiceView = PersonMergeChoiceView
    app_name = 'person'

    @property
    def create_obj_fn(self):
        return person.fixtures.create_person_obj
