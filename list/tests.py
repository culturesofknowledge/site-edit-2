from django.test import TestCase
from django.urls import reverse

from core.models import CofkUserSavedQuery
from login.fixtures import create_test_user


def create_saved_query(user, title='my query') -> CofkUserSavedQuery:
    return CofkUserSavedQuery.objects.create(
        username=user, query_class='work', query_method='search', query_title=title,
        query_order_by='iwork_id', query_sort_descending=0, query_entries_per_page=20,
        query_record_layout='table')


class SavedQueriesTests(TestCase):

    def setUp(self):
        self.owner = create_test_user('owner@example.org')
        self.other = create_test_user('other@example.org')
        self.query = create_saved_query(self.owner)
        self.url = reverse('list:savedqueries')

    def test_requires_login(self):
        response = self.client.post(self.url, {'query_id': self.query.pk, 'delete': '1'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CofkUserSavedQuery.objects.filter(pk=self.query.pk).exists())

    def test_cannot_delete_other_users_query(self):
        self.client.force_login(self.other)

        self.client.post(self.url, {'query_id': self.query.pk, 'delete': '1'})

        self.assertTrue(CofkUserSavedQuery.objects.filter(pk=self.query.pk).exists())

    def test_cannot_rename_other_users_query(self):
        self.client.force_login(self.other)

        self.client.post(self.url, {'query_id': self.query.pk, 'save': '1', 'query_title': 'hijacked'})

        self.query.refresh_from_db()
        self.assertEqual(self.query.query_title, 'my query')

    def test_owner_can_rename_and_delete(self):
        self.client.force_login(self.owner)

        self.client.post(self.url, {'query_id': self.query.pk, 'save': '1', 'query_title': 'renamed'})
        self.query.refresh_from_db()
        self.assertEqual(self.query.query_title, 'renamed')

        self.client.post(self.url, {'query_id': self.query.pk, 'delete': '1'})
        self.assertFalse(CofkUserSavedQuery.objects.filter(pk=self.query.pk).exists())

    def test_list_shows_only_own_queries(self):
        create_saved_query(self.other, title='other query')
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual([q.pk for q in response.context['object_list']], [self.query.pk])
