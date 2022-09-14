from person import fixtures as person_fixtures
from person.models import CofkUnionPerson
from siteedit2.utils import test_utils
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form


class PersonInitFormTest(EmloSeleniumTestCase):

    def test_create_person(self):
        self.selenium.get(self.get_url_by_viewname('person:init_form'))

        self.fill_form_by_dict(person_fixtures.person_min_dict_a.items(), )

        new_id = simple_test_create_form(self, CofkUnionPerson)

        person = CofkUnionPerson.objects.get(iperson_id=new_id)
        self.assertEqual(person.foaf_name,
                         person_fixtures.person_min_dict_a.get('foaf_name'))

    def test_full_form__GET_simple(self):
        person = CofkUnionPerson(**person_fixtures.person_dict_a)
        person.save()
        url = self.get_url_by_viewname('person:full_form',
                                       kwargs={'iperson_id': person.iperson_id})
        test_utils.simple_test_full_form__GET(
            self, person,
            url, [
                'foaf_name', 'skos_altlabel', 'person_aliases',
                'further_reading', 'editors_notes',
                'gender',
            ]
        )

    def test_full_form__POST_simple(self):
        pass
