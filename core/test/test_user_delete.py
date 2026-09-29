from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core import constant
from core.helper import perm_serv
from core.models import CofkUserSavedQuery, CofkUserSavedQuerySelection
from login.fixtures import create_test_user
from login.models import CofkUser
from work.models import CofkUnionWork


class TestUserDelete(TestCase):

    def setUp(self):
        # the user form lists the roles, so they must exist
        for role, _ in constant.ROLE_DISPLAY_NAMES:
            Group.objects.get_or_create(name=role)
        cache.clear()

        self.supervisor = create_test_user('supervisor@example.org')
        self.supervisor.user_permissions.add(perm_serv.get_perm_by_full_name(constant.PM_CHANGE_USER))
        self.target = create_test_user('student@example.org')
        self.client.force_login(self.supervisor)

    def delete_url(self, username):
        return reverse('user:delete', args=[username])

    def create_saved_query(self, user: CofkUser) -> CofkUserSavedQuery:
        query = CofkUserSavedQuery.objects.create(
            username=user, query_class='work', query_method='search', query_title='',
            query_order_by='iwork_id', query_sort_descending=0, query_entries_per_page=20,
            query_record_layout='table')
        CofkUserSavedQuerySelection.objects.create(query=query, column_name='iwork_id', column_value='1', op_name='eq',
                                                   op_value='1', column_value2='')
        return query

    def test_edit_form_shows_delete_button(self):
        response = self.client.get(reverse('user:full_form', args=[self.target.username]))
        self.assertContains(response, self.delete_url(self.target.username))

    def test_edit_form_hides_delete_button_for_own_account(self):
        response = self.client.get(reverse('user:full_form', args=[self.supervisor.username]))
        self.assertNotContains(response, self.delete_url(self.supervisor.username))

    def test_confirm_page_lists_records(self):
        CofkUnionWork.objects.create(work_id='work_test_1', creation_user=self.target.username,
                                     change_user='someone else')
        self.create_saved_query(self.target)

        response = self.client.get(self.delete_url(self.target.username))

        self.assertContains(response, '1 works')
        self.assertContains(response, 'saved queries of this user will be deleted')

    def test_delete_keeps_records_and_removes_saved_queries(self):
        work = CofkUnionWork.objects.create(work_id='work_test_1', creation_user=self.target.username,
                                            change_user=self.target.username)
        query = self.create_saved_query(self.target)

        response = self.client.post(self.delete_url(self.target.username))

        self.assertRedirects(response, reverse('user:search') + '?to_user_messages='
                             + 'User%20%22student%40example.org%22%20deleted%20successfully',
                             fetch_redirect_response=False)
        self.assertFalse(CofkUser.objects.filter(pk=self.target.username).exists())
        self.assertFalse(CofkUserSavedQuery.objects.filter(pk=query.pk).exists())
        self.assertFalse(CofkUserSavedQuerySelection.objects.filter(query_id=query.pk).exists())
        work.refresh_from_db()
        self.assertEqual(work.creation_user, self.target.username)

    def test_cannot_delete_own_account(self):
        response = self.client.post(self.delete_url(self.supervisor.username))

        self.assertRedirects(response, reverse('user:full_form', args=[self.supervisor.username]),
                             fetch_redirect_response=False)
        self.assertTrue(CofkUser.objects.filter(pk=self.supervisor.username).exists())

    def test_requires_change_user_permission(self):
        self.client.force_login(create_test_user('editor@example.org'))

        response = self.client.post(self.delete_url(self.target.username))

        # permission denied is handled by redirecting to the dashboard (see handler403)
        self.assertRedirects(response, reverse('login:dashboard'), fetch_redirect_response=False)
        self.assertTrue(CofkUser.objects.filter(pk=self.target.username).exists())

    def test_unknown_user_is_404(self):
        response = self.client.post(self.delete_url('nobody@example.org'))
        self.assertEqual(response.status_code, 404)
