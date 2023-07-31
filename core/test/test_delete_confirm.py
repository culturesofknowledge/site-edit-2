from django.urls import reverse

from location.fixtures import create_location_a
from person.fixtures import create_person_obj
from publication.models import CofkUnionPublication
from siteedit2.serv.test_serv import EmloSeleniumTestCase


class TestDeleteConfirm(EmloSeleniumTestCase):

    def assert_delete_confirm(self, obj, app_name, obj_id):
        obj.refresh_from_db()  # make sure it's in the db

        self.goto_path(reverse(f'{app_name}:full_form', args=[obj_id]))

        del_path = reverse(f'{app_name}:delete', args=[obj_id])
        self.js_click(f'a[href="{del_path}"]')

        self.find_element_by_css('#confirm-label').click()

        self.find_element_by_css('#del-btn').click()

        with self.assertRaises(obj.DoesNotExist):
            obj.refresh_from_db()

    def test_person_delete_confirm(self):
        fixture_person = create_person_obj()
        fixture_person.save()

        self.assert_delete_confirm(fixture_person, 'person', fixture_person.iperson_id)

    def test_location_delete_confirm(self):
        fixture_location = create_location_a()
        fixture_location.save()

        self.assert_delete_confirm(fixture_location, 'location', fixture_location.location_id)

    def test_pub_delete_confirm(self):
        fixture_pub = CofkUnionPublication()
        fixture_pub.publication_details = 'test'
        fixture_pub.abbrev = 'test'
        fixture_pub.save()

        self.assert_delete_confirm(fixture_pub, 'publication', fixture_pub.publication_id)
