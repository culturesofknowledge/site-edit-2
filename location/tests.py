from typing import TYPE_CHECKING, Type

import bs4
from django.urls import reverse
from selenium.webdriver.common.by import By

import location.fixtures
import location.fixtures
from core.helper import model_utils, url_utils
from location.models import CofkUnionLocation, CofkLocationResourceMap
from location.recref_adapter import LocationResourceRecrefAdapter
from location.views import LocationMergeChoiceView
from siteedit2.utils import test_utils
from siteedit2.utils.test_utils import EmloSeleniumTestCase, simple_test_create_form, MultiM2MTester, ResourceM2MTester, \
    CommentM2MTester, CommonSearchTests, MergeTests

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


class LocationMergeTests(MergeTests):
    ResourceRecrefAdapter: Type['TargetResourceRecrefAdapter'] = LocationResourceRecrefAdapter
    RecrefResourceMap: Type['Recref'] = CofkLocationResourceMap
    ChoiceView = LocationMergeChoiceView
    app_name = 'location'

    @property
    def create_obj_fn(self):
        return location.fixtures.create_location_a

    def prepare_data(self):
        objs = [self.create_obj_fn() for _ in range(3)]
        for m in objs:
            m.save()

        for m in objs:
            test_utils.add_resources_by_msgs(self.resource_msg_list, m, self.ResourceRecrefAdapter)

        return objs

    def test_merge_action(self):
        other_models = self.prepare_data()
        loc_a = other_models.pop()

        # test response
        self.assertEqual(test_utils.cnt_recref(self.RecrefResourceMap, loc_a),
                         len(self.resource_msg_list))
        response = self.client.post(reverse(f'{self.app_name}:merge_action'), data={
            'selected_pk': loc_a.pk,
            'merge_pk': [m.pk for m in other_models],
            'action_type': 'confirm',
        })
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_utils.cnt_recref(self.RecrefResourceMap, loc_a),
                         (len(other_models) + 1) * len(self.resource_msg_list))
        self.assertTrue(not any(
            m._meta.model.objects.filter(pk=m.pk).exists()
            for m in other_models
        ))

    def test_merge_choice(self):
        objs = self.prepare_data()
        url = reverse(f'{self.app_name}:merge')
        url = url_utils.build_url_query(url, [
            ('__merge_id', self.ChoiceView.get_id_field().field.value_from_object(m))
            for m in objs
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = bs4.BeautifulSoup(response.content, features="html.parser")
        self.assertEqual(len(soup.select('.merge-items')), len(objs))

    def test_merge_confirm(self):
        other_models = self.prepare_data()
        loc_a = other_models.pop()
        url = reverse(f'{self.app_name}:merge_confirm')
        response = self.client.post(url, data={
            'selected_pk': loc_a.pk,
            'merge_pk': [m.pk for m in other_models],
        })
        self.assertEqual(response.status_code, 200)
        soup = bs4.BeautifulSoup(response.content, features="html.parser")
        self.assertEqual(len(soup.select('.merge-items')), len(other_models) + 1)
