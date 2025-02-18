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

def is_user_editor_or_supervisor(user):
    return user.groups.filter(name__in=[constant.ROLE_EDITOR, constant.ROLE_SUPER]).exists()
