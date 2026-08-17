from django.test import TestCase, RequestFactory
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse
from django.utils import timezone

from core import constant
from core.helper import webdriver_actions, perm_serv
from core.helper.test_serv import EmloSeleniumTestCase
from login.fixtures import create_test_user, create_test_user__a


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
