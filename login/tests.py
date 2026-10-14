from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from core import constant
from core.helper import webdriver_actions, perm_serv
from core.helper.test_serv import EmloSeleniumTestCase
from login import utils as login_utils
from login.fixtures import create_test_user, create_test_user__a
from login.models import CofkUser


class LoginTimesTest(TestCase):

    def setUp(self):
        self.user = create_test_user('test_login_times')
        self.request = RequestFactory().get('/')

    def test_first_login_sets_login_time(self):
        self.assertIsNone(self.user.login_time)
        self.assertIsNone(self.user.prev_login)

        user_logged_in.send(sender=self.user.__class__, request=self.request, user=self.user)
        self.user.refresh_from_db()

        self.assertIsNotNone(self.user.login_time)
        self.assertIsNone(self.user.prev_login)

    def test_second_login_shifts_login_time_to_prev_login(self):
        first_login = timezone.now()
        self.user.login_time = first_login
        self.user.save(update_fields=['login_time'])

        user_logged_in.send(sender=self.user.__class__, request=self.request, user=self.user)
        self.user.refresh_from_db()

        self.assertEqual(self.user.prev_login, first_login)
        self.assertGreater(self.user.login_time, first_login)


class FailedLoginsTest(TestCase):

    def setUp(self):
        self.user = create_test_user('test_failed_logins')
        self.request = RequestFactory().get('/')

    def test_failed_login_increments_counter(self):
        self.assertEqual(self.user.failed_logins, 0)

        user_login_failed.send(sender=__name__, credentials={'username': self.user.username},
                               request=self.request)
        self.user.refresh_from_db()

        self.assertEqual(self.user.failed_logins, 1)

    def test_repeated_failed_logins_accumulate(self):
        for _ in range(3):
            user_login_failed.send(sender=__name__, credentials={'username': self.user.username},
                                   request=self.request)
        self.user.refresh_from_db()

        self.assertEqual(self.user.failed_logins, 3)

    def test_failed_login_for_unknown_username_does_not_raise(self):
        # credentials.username won't always match a real account (e.g. a
        # typo'd or made-up login attempt) -- this must not error out.
        user_login_failed.send(sender=__name__, credentials={'username': 'no_such_user'},
                               request=self.request)

    def test_failed_login_without_username_does_not_raise(self):
        user_login_failed.send(sender=__name__, credentials={}, request=self.request)


class SuperuserPrivilegesTest(TestCase):
    """A superuser has access to all features, so the group based role checks
    must accept it without the 'super' group being assigned.
    """

    def setUp(self):
        self.superuser = create_test_user('test_superuser_privileges')
        self.superuser.is_superuser = True
        self.superuser.is_staff = True
        self.superuser.save()

        self.plain_user = create_test_user('test_plain_user')

    def test_superuser_is_supervisor_without_group(self):
        self.assertFalse(self.superuser.groups.exists())
        self.assertTrue(self.superuser.is_supervisor)
        self.assertTrue(login_utils.is_user_supervisor(self.superuser))
        self.assertTrue(login_utils.is_user_editor_or_supervisor(self.superuser))

    def test_inactive_superuser_is_not_supervisor(self):
        self.superuser.is_active = False
        self.superuser.save()

        self.assertFalse(self.superuser.is_supervisor)
        self.assertFalse(login_utils.is_user_supervisor(self.superuser))

    def test_plain_user_is_not_supervisor(self):
        self.assertFalse(self.plain_user.is_supervisor)
        self.assertFalse(login_utils.is_user_supervisor(self.plain_user))

    def test_group_member_is_still_supervisor(self):
        group, _ = Group.objects.get_or_create(name=constant.ROLE_SUPER)
        self.plain_user.groups.add(group)

        self.assertTrue(self.plain_user.is_supervisor)
        self.assertTrue(login_utils.is_user_supervisor(self.plain_user))


class CreateSuperuserFieldsTest(TestCase):
    """forename, surname and email are REQUIRED_FIELDS, so createsuperuser asks
    for them (interactively) / accepts them as options.
    """

    def test_names_and_email_are_stored(self):
        call_command('createsuperuser', username='test_createsuperuser', forename='Ann',
                     surname='Lee', email='ann@example.com', interactive=False, verbosity=0)

        user = CofkUser.objects.get(pk='test_createsuperuser')

        self.assertEqual(user.forename, 'Ann')
        self.assertEqual(user.surname, 'Lee')
        self.assertEqual(user.email, 'ann@example.com')
        self.assertTrue(user.is_superuser)


class TestPermission(EmloSeleniumTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login_user = None

    def assert_audit_permission(self, user, has_perm: bool):
        self.goto_vname('login:gate')
        webdriver_actions.login(self.selenium, user.username, user.raw_password)

        self.goto_vname('audit:search')
        if has_perm:
            assert not webdriver_actions.is_403(self.selenium)
        else:
            # Permission denied redirects to dashboard (not a 403 page)
            dashboard_path = reverse('login:dashboard')
            assert self.selenium.current_url.endswith(dashboard_path), (
                f"Expected redirect to dashboard, got {self.selenium.current_url}"
            )

        self.goto_vname('login:dashboard')
        assert not webdriver_actions.is_403(self.selenium)

    def test_audit_search__403(self):
        user = create_test_user('test_user_x1', raw_password='pass')
        self.assert_audit_permission(user, has_perm=False)

    def test_audit_search__with_perm(self):
        user = create_test_user('test_user_x1', raw_password='pass')
        user.user_permissions.add(perm_serv.get_perm_by_full_name(constant.PM_VIEW_AUDIT))
        user.save()
        self.assert_audit_permission(user, has_perm=True)

        superuser = create_test_user__a()
        self.assert_audit_permission(superuser, has_perm=True)
