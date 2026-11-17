from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from core import constant
from core.helper import webdriver_actions, perm_serv
from core.helper.test_serv import EmloSeleniumTestCase
from core.models import CofkUserSavedQuery
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


def create_test_user_with_email(username, email) -> CofkUser:
    user = create_test_user(username, is_save=False)
    user.email = email
    user.save()
    return user


class GenerateUsernameTest(TestCase):

    def test_from_names(self):
        self.assertEqual(login_utils.generate_username(' Anne Marie ', 'Dupré', 'x@example.com'), 'anne-marie.dupre')

    def test_from_one_name(self):
        self.assertEqual(login_utils.generate_username('', 'Lee', 'x@example.com'), 'lee')

    def test_from_email_without_names(self):
        self.assertEqual(login_utils.generate_username('', '  ', 'Ann.Lee@example.com'), 'ann.lee')

    def test_number_added_when_taken_ignoring_case(self):
        create_test_user('Ann.Lee')
        create_test_user('ann.lee2')
        self.assertEqual(login_utils.generate_username('Ann', 'Lee', None), 'ann.lee3')


class CaseInsensitiveUsernameTest(TestCase):

    def test_username_differing_only_by_case_is_rejected(self):
        create_test_user('Bob')
        with self.assertRaises(ValidationError):
            create_test_user('bob')


class RenameUserTest(TestCase):

    def setUp(self):
        self.user = create_test_user('old_name')
        self.group, _ = Group.objects.get_or_create(name=constant.ROLE_EDITOR)
        self.user.groups.add(self.group)
        self.user.user_permissions.add(perm_serv.get_perm_by_full_name(constant.PM_VIEW_AUDIT))
        self.query = CofkUserSavedQuery.objects.create(
            username=self.user, query_class='work', query_method='search', query_title='',
            query_order_by='iwork_id', query_sort_descending=0, query_entries_per_page=20,
            query_record_layout='table')

    def test_rename_moves_references(self):
        CofkUser.rename('old_name', 'new_name')

        self.assertFalse(CofkUser.objects.filter(pk='old_name').exists())
        user = CofkUser.objects.get(pk='new_name')
        self.assertEqual(list(user.groups.all()), [self.group])
        self.assertTrue(user.has_perm(constant.PM_VIEW_AUDIT))
        self.query.refresh_from_db()
        self.assertEqual(self.query.username_id, 'new_name')

    def test_rename_to_existing_username_is_rejected(self):
        other = create_test_user('Other_Name')
        with self.assertRaises(ValidationError):
            CofkUser.rename('old_name', 'other_name')

        self.assertTrue(CofkUser.objects.filter(pk='old_name').exists())
        other.refresh_from_db()
        self.assertEqual(other.username, 'Other_Name')

    def test_case_only_rename_is_allowed(self):
        CofkUser.rename('old_name', 'Old_Name')
        self.assertTrue(CofkUser.objects.filter(pk='Old_Name').exists())


class LoginWithUsernameOrEmailTest(TestCase):

    def setUp(self):
        self.user = create_test_user_with_email('ann.lee', 'ann@example.com')

    def login(self, login, password='pass'):
        return self.client.post(reverse('login:gate'), {'username': login, 'password': password})

    def test_login_with_username(self):
        self.assertRedirects(self.login('ann.lee'), reverse('login:dashboard'), fetch_redirect_response=False)

    def test_login_with_username_ignores_case(self):
        self.assertRedirects(self.login('Ann.Lee'), reverse('login:dashboard'), fetch_redirect_response=False)

    def test_login_with_email(self):
        self.assertRedirects(self.login('ANN@example.com'), reverse('login:dashboard'), fetch_redirect_response=False)

    def test_username_wins_over_email(self):
        # another user whose username is ann's email address
        create_test_user_with_email('ann@example.com', 'other@example.com')
        self.login('ann@example.com')
        self.assertEqual(self.client.session['_auth_user_id'], 'ann@example.com')

    def test_wrong_password(self):
        response = self.login('ann@example.com', password='wrong')
        self.assertContains(response, 'Incorrect username/email or password')

    def test_shared_email_asks_for_username(self):
        create_test_user_with_email('ann.lee2', 'ann@example.com')

        response = self.login('ann@example.com')

        self.assertContains(response, 'Please log in with your username instead')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.login('ann.lee2'), reverse('login:dashboard'), fetch_redirect_response=False)

    def test_failed_login_with_email_increments_counter(self):
        self.login('ann@example.com', password='wrong')
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_logins, 1)


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
