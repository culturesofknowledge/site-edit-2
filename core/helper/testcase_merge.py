import unittest
from typing import Type, Callable

import bs4
from django.urls import reverse
from django.views import View

from core.helper import url_serv
from core.helper.test_serv import LoginTestCase, add_resources_by_msgs, cnt_recref
from core.models import Recref


class MergeTests(LoginTestCase):
    RecrefResourceMap: Type['Recref'] = None
    ChoiceView: Type['View'] = None
    app_name: str = None
    resource_msg_list = ['aaaaa', 'bbbb', 'ccc']

    def setUp(self) -> None:
        if type(self) is MergeTests:
            raise unittest.SkipTest("MergeTests is an abstract class and should not be run directly")
        super().setUp()

    @property
    def create_obj_fn(self) -> Callable:
        raise NotImplementedError()

    def prepare_data(self):
        objs = [self.create_obj_fn() for _ in range(3)]
        for m in objs:
            m.save()

        for m in objs:
            add_resources_by_msgs(self.resource_msg_list, m)

        return objs

    def test_merge_action(self):
        other_models = self.prepare_data()
        loc_a = other_models.pop()

        # test response
        self.assertEqual(cnt_recref(self.RecrefResourceMap, loc_a),
                         len(self.resource_msg_list))
        response = self.client.post(reverse(f'{self.app_name}:merge_action'), data={
            'selected_pk': loc_a.pk,
            'merge_pk': [m.pk for m in other_models],
            'action_type': 'confirm',
        })
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cnt_recref(self.RecrefResourceMap, loc_a),
                         (len(other_models) + 1) * len(self.resource_msg_list))
        self.assertTrue(not any(
            m._meta.model.objects.filter(pk=m.pk).exists()
            for m in other_models
        ))

    def test_merge_choice(self):
        objs = self.prepare_data()
        url = reverse(f'{self.app_name}:merge')
        url = url_serv.build_url_query(url, [
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
