from core import constant
from core.helper import webdriver_actions, perm_serv
from login.fixtures import create_test_user, create_test_user__a
from siteedit2.serv.test_serv import EmloSeleniumTestCase


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
            assert webdriver_actions.is_403(self.selenium)

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
