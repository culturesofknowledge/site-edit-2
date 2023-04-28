import dataclasses
from functools import wraps

from django.core.exceptions import PermissionDenied

from login.models import CofkUser


@dataclasses.dataclass
class PermissionData:
    app_label: str
    codename: str

    @property
    def full_name(self):
        return f'{self.app_label}.{self.codename}'

    @classmethod
    def from_full_name(cls, full_name):
        app_name, code_name = full_name.split('.')
        return cls(app_name, code_name)


def class_permission_required(perms: str | list[str]):
    """
    permission checking for post / get method of class based view
    """
    if isinstance(perms, str):
        perms = [perms]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            for arg in args:
                user = getattr(arg, 'user', None)
                if user is not None and isinstance(user, CofkUser) and user.has_perms(perms):
                    return view_func(*args, **kwargs)

            raise PermissionDenied()

        return _wrapped_view

    return decorator


def validate_permission_denied(user: CofkUser, perms: str | list[str]):
    if perms is not None and not user.has_perms(perms):
        raise PermissionDenied()
