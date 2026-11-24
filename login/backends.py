from django.contrib.auth.backends import ModelBackend

from login import utils as login_utils
from login.models import CofkUser


class UsernameOrEmailBackend(ModelBackend):
    """Log in with the username or, failing that, the email address.

    An email address shared by several accounts does not log in to any of
    them -- CustomAuthenticationForm asks for the username instead.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(CofkUser.USERNAME_FIELD)
        if username is None or password is None:
            return None

        users = login_utils.find_users_by_login(username)
        if len(users) != 1:
            # run the password hasher anyway, so an unknown login takes as
            # long as a wrong password (same as ModelBackend)
            CofkUser().set_password(password)
            return None

        user = users[0]
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
