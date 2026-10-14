from login.models import CofkUser
from core import constant


def get_users_by_groups(group_names: list):
    """
    Fetch users who belong to the specified groups.
    Args:
        group_names (list): A list of group names.
    Returns:
        QuerySet: A distinct QuerySet of CofkUser objects.
    """
    return CofkUser.objects.filter(groups__name__in=group_names).distinct()

def get_contributing_editors():
    return get_users_by_groups([constant.ROLE_CONTRIBUTING_EDITOR, constant.ROLE_SUPER])

def is_superuser(user):
    """A superuser has access to all features, so every role check below
    accepts it -- mirroring how Django's own has_perm() treats is_superuser.
    """
    return bool(getattr(user, 'is_active', False) and getattr(user, 'is_superuser', False))

def is_user_editor_or_supervisor(user):
    if is_superuser(user):
        return True
    return user.groups.filter(name__in=[constant.ROLE_EDITOR, constant.ROLE_SUPER]).exists()

def is_user_supervisor(user):
    if is_superuser(user):
        return True
    return user.groups.filter(name__in=[constant.ROLE_SUPER]).exists()
