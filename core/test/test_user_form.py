from django.contrib.auth.models import Group
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core import constant
from core.helper import perm_serv
from login.fixtures import create_test_user
from login.models import CofkUser


class TestUserForm(TestCase):

    def setUp(self):
        # the user form lists the roles, so they must exist
        for role, _ in constant.ROLE_DISPLAY_NAMES:
            Group.objects.get_or_create(name=role)
        cache.clear()

        self.supervisor = create_test_user('supervisor', is_save=False)
        self.supervisor.forename, self.supervisor.surname = 'Sue', 'Visor'
        self.supervisor.email = 'supervisor@example.com'
        self.supervisor.save()
        self.supervisor.user_permissions.add(perm_serv.get_perm_by_full_name(constant.PM_CHANGE_USER))
        self.client.force_login(self.supervisor)

    def create_user(self, email='ann@example.com', forename='Ann', surname='Lee'):
        return self.client.post(reverse('user:init_form'), {
            'email': email, 'forename': forename, 'surname': surname, 'is_active': '1',
        }, follow=True)

    def edit_user(self, username, new_username, **kwargs):
        user = CofkUser.objects.get(pk=username)
        return self.client.post(reverse('user:full_form', args=[username]), {
            'username': new_username, 'email': user.email, 'forename': user.forename, 'surname': user.surname,
            'is_active': '1', **kwargs,
        })

    def test_create_generates_username_and_shows_it(self):
        response = self.create_user()

        self.assertTrue(CofkUser.objects.filter(pk='ann.lee').exists())
        self.assertContains(response, 'New user created with the username <strong>ann.lee</strong>')

    def test_create_emails_username(self):
        self.create_user()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your EMLO editing account')
        self.assertIn('Your username is: ann.lee', mail.outbox[0].body)

    def test_accounts_can_share_email(self):
        self.create_user()
        self.create_user()

        self.assertEqual(sorted(CofkUser.objects.filter(email='ann@example.com').values_list('pk', flat=True)),
                         ['ann.lee', 'ann.lee2'])

    def test_rename(self):
        self.create_user()

        response = self.edit_user('ann.lee', 'alee')

        self.assertRedirects(response, reverse('user:full_form', args=['alee']))
        self.assertFalse(CofkUser.objects.filter(pk='ann.lee').exists())
        self.assertEqual(CofkUser.objects.get(pk='alee').email, 'ann@example.com')

    def test_rename_to_taken_username_is_rejected(self):
        create_test_user('Other')
        self.create_user()

        response = self.edit_user('ann.lee', 'other')

        self.assertContains(response, 'The username &quot;other&quot; is already taken.')
        self.assertTrue(CofkUser.objects.filter(pk='ann.lee').exists())
        self.assertIsNone(CofkUser.objects.get(pk='Other').email)

    def test_rename_rejects_invalid_characters(self):
        self.create_user()

        response = self.edit_user('ann.lee', 'ann lee')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(CofkUser.objects.filter(pk='ann.lee').exists())

    def test_renaming_yourself_keeps_you_logged_in(self):
        self.edit_user('supervisor', 'boss')

        response = self.client.get(reverse('user:full_form', args=['boss']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].pk, 'boss')
