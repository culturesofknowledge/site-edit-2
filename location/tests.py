from pathlib import Path
from typing import TYPE_CHECKING, Type

from django.test import TestCase
from django.urls import reverse
from selenium.webdriver.common.by import By

import location.fixtures
from cllib import path_utils
from core import constant
from core.helper import model_serv, test_serv, perm_serv
from core.helper.test_serv import EmloSeleniumTestCase, simple_test_create_form, MultiM2MTester, ResourceM2MTester, \
    CommentM2MTester, CommonSearchTests, MergeTests
from core.helper.view_components import DownloadCsvHandler
from location.models import CofkUnionLocation, CofkLocationResourceMap
from location.recref_adapter import LocationResourceRecrefAdapter
from location.views import LocationMergeChoiceView, LocationCsvHeaderValues
from login.fixtures import create_test_user

if TYPE_CHECKING:
    from core.helper.common_recref_adapter import TargetResourceRecrefAdapter
    from core.models import Recref


class LocationFormTests(EmloSeleniumTestCase):

    def test_create_location(self):
        self.goto_vname('location:init_form')

        self.fill_form_by_dict(location.fixtures.location_dict_a.items(),
                               exclude_fields=['location_name'], )

        new_id = simple_test_create_form(self, CofkUnionLocation)

        loc = CofkUnionLocation.objects.get(location_id=new_id)
        self.assertEqual(loc.element_1_eg_room, location.fixtures.location_dict_a.get('element_1_eg_room'))

    def test_full_form__GET(self):
        loc_a = location.fixtures.create_location_a()
        loc_a.save()
        url = self.get_url_by_viewname('location:full_form',
                                       location_id=loc_a.location_id)
        test_serv.simple_test_full_form__GET(
            self, loc_a,
            url, ['editors_notes', 'element_1_eg_room', 'element_4_eg_city', 'latitude']
        )

    def test_full_form__POST(self):
        loc_a = location.fixtures.create_location_a()
        loc_a.save()

        m2m_tester = MultiM2MTester(m2m_tester_list=[
            ResourceM2MTester(self, loc_a.cofklocationresourcemap_set, formset_prefix='res'),
            CommentM2MTester(self, loc_a.cofklocationcommentmap_set, formset_prefix='comment'),
        ])

        # update web page
        url = self.get_url_by_viewname('location:full_form',
                                       location_id=loc_a.location_id)
        self.selenium.get(url)

        # fill m2m
        m2m_tester.fill()

        self.click_submit()

        # assert result after form submit
        loc_a.refresh_from_db()

        # assert m2m tester
        m2m_tester.assert_after_update()


def prepare_loc_records() -> list[CofkUnionLocation]:
    return model_serv.create_multi_records_by_dict_list(CofkUnionLocation, (
        location.fixtures.location_dict_a,
        location.fixtures.location_dict_b,
    ))


class LocationCommonSearchTests(EmloSeleniumTestCase, CommonSearchTests):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_common_search_test(self, 'location:search', prepare_loc_records)

    def test_search__search_unique(self):
        def _fill(target_record):
            ele = self.selenium.find_element(By.ID, 'id_location_id')
            ele.send_keys(target_record.location_id)

        def _check(target_record):
            self.assertIn(target_record.location_name,
                          self.find_table_col_element(0, 0).text)

        self._test_search__search_unique(_fill, _check)


class LocationMergeTests(MergeTests):
    ResourceRecrefAdapter: Type['TargetResourceRecrefAdapter'] = LocationResourceRecrefAdapter
    RecrefResourceMap: Type['Recref'] = CofkLocationResourceMap
    ChoiceView = LocationMergeChoiceView
    app_name = 'location'

    @property
    def create_obj_fn(self):
        return location.fixtures.create_location_a


class LocationDownloadCsvHandlerTests(TestCase):
    def test_create_csv_file(self):
        queryset = CofkUnionLocation.objects.all()[:10]
        record_size = queryset.count()
        csv_path = path_utils.create_tmp_path()
        csv_handler = DownloadCsvHandler(LocationCsvHeaderValues())
        csv_handler.create_csv_file(queryset, csv_path)

        csv_text = Path(csv_path).read_text()
        self.assertGreater(len(csv_text.splitlines()), record_size)


class LocationCsvExportTests(TestCase):

    def location_name_cell(self, location: CofkUnionLocation) -> str:
        location.save()
        location.sent = location.recd = location.all_works = location.mentioned = 0
        return list(LocationCsvHeaderValues().obj_to_values(location))[0]

    def test_location_name_includes_synonyms(self):
        # emlo-project#857: as in old EMLO edit, alternative names in brackets on the next line
        location = CofkUnionLocation(location_name='Oxford', location_synonyms='Oxon\nOxonia')
        self.assertEqual(self.location_name_cell(location), 'Oxford\n(Oxon\nOxonia)')

    def test_location_name_without_synonyms(self):
        location = CofkUnionLocation(location_name='Oxford')
        self.assertEqual(self.location_name_cell(location), 'Oxford')


class LocationDeletePermissionTests(TestCase):

    def setUp(self):
        self.location = location.fixtures.create_location_a()
        self.location.save()
        self.delete_url = reverse('location:delete', args=[self.location.location_id])

    def test_delete_requires_login(self):
        response = self.client.post(self.delete_url)

        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(CofkUnionLocation.objects.filter(pk=self.location.pk).exists())

    def test_delete_requires_change_location_permission(self):
        self.client.force_login(create_test_user('viewer'))

        response = self.client.post(self.delete_url)

        # permission denied is handled by redirecting to the dashboard (see handler403)
        self.assertRedirects(response, reverse('login:dashboard'), fetch_redirect_response=False)
        self.assertTrue(CofkUnionLocation.objects.filter(pk=self.location.pk).exists())

    def test_delete_with_change_location_permission(self):
        editor = create_test_user('editor')
        editor.user_permissions.add(perm_serv.get_perm_by_full_name(constant.PM_CHANGE_LOCATION))
        self.client.force_login(editor)

        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(CofkUnionLocation.objects.filter(pk=self.location.pk).exists())
