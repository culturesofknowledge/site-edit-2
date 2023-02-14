from typing import TYPE_CHECKING, Type

from django.urls import reverse
from selenium.webdriver.common.by import By

import location.fixtures
import location.fixtures
from core.helper import model_utils
from location.models import CofkUnionLocation, CofkLocationResourceMap
from location.recref_adapter import LocationResourceRecrefAdapter
from siteedit2.utils import test_utils
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form, MultiM2MTester, ResourceM2MTester, \
    CommentM2MTester, CommonSearchTests, LoginTestCase

if TYPE_CHECKING:
    from core.helper.common_recref_adapter import TargetResourceRecrefAdapter
    from core.models import Recref


class LocationFormTests(EmloSeleniumTestCase):
    # KTODO test validate fail
    # KTODO test upload images

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
        test_utils.simple_test_full_form__GET(
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
    return model_utils.create_multi_records_by_dict_list(CofkUnionLocation, (
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
            self.assertEqual(self.find_table_col_element(0, 0).text,
                             target_record.location_name)

        self._test_search__search_unique(_fill, _check)


class LocationMergeTests(LoginTestCase):
    ResourceRecrefAdapter: Type['TargetResourceRecrefAdapter'] = LocationResourceRecrefAdapter
    RecrefResourceMap: Type['Recref'] = CofkLocationResourceMap
    app_name = 'location'

    @property
    def create_obj_fn(self):
        return location.fixtures.create_location_a

    def test_merge_action(self):
        loc_a = self.create_obj_fn()
        loc_a.save()

        other_models = [self.create_obj_fn() for _ in range(2)]
        resource_msg_list = ['aaaaa', 'bbbb', 'ccc']
        for m in other_models:
            m.save()
            test_utils.add_resources_by_msgs(resource_msg_list, m, self.ResourceRecrefAdapter)

        # test response
        self.assertEqual(test_utils.cnt_recref(self.RecrefResourceMap, loc_a), 0)
        response = self.client.post(reverse(f'{self.app_name}:merge_action'), data={
            'selected_pk': loc_a.pk,
            'merge_pk': [m.pk for m in other_models],
            'action_type': 'confirm',
        })
        print(response)
        self.assertEqual(test_utils.cnt_recref(self.RecrefResourceMap, loc_a),
                         len(other_models) * len(resource_msg_list))

        self.assertTrue(not any(
            m._meta.model.objects.filter(pk=m.pk).exists()
            for m in other_models
        ))
