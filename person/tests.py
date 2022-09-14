from person import fixtures
from person.models import CofkUnionPerson
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form


class PersonInitFormTest(EmloSeleniumTestCase):

    def test_create_person(self):
        self.selenium.get(self.get_url_by_viewname('person:init_form'))

        self.fill_form_by_dict(fixtures.person_min_dict_a.items(), )

        new_id = simple_test_create_form(self, CofkUnionPerson)

        person = CofkUnionPerson.objects.get(iperson_id=new_id)
        self.assertEqual(person.foaf_name,
                         fixtures.person_min_dict_a.get('foaf_name'))
