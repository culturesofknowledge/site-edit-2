import re
import unicodedata

from login.models import CofkUser
from core import constant


def _clean_username_part(value: str | None) -> str:
    # "Anne-Marie  Dupré" -> "anne-marie-dupre"
    value = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'\s+', '-', value.strip().lower())
    return re.sub(r'[^a-z0-9._-]+', '', value).strip('._-')


def generate_username(forename: str | None, surname: str | None, email: str | None) -> str:
    """Build a unique username for a new user: "forename.surname", or the part
    of the email before the @ when there are no usable names. A number is added
    when the name is taken (case-insensitively): ann.lee, ann.lee2, ann.lee3 ...
    """
    max_length = CofkUser._meta.get_field('username').max_length
    names = [p for p in (_clean_username_part(forename), _clean_username_part(surname)) if p]
    base = ('.'.join(names) or _clean_username_part((email or '').split('@')[0]) or 'user')[:max_length]

    username = base
    num = 2
    while CofkUser.objects.filter(username__iexact=username).exists():
        suffix = str(num)
        username = base[:max_length - len(suffix)] + suffix
        num += 1
    return username


def find_users_by_login(login: str | None) -> list[CofkUser]:
    """Users matching what was typed in the login box. A username match
    wins, exact case first; otherwise every user with that email address,
    which can be more than one since accounts may share an email.
    """
    login = (login or '').strip()
    if not login:
        return []

    user = CofkUser.objects.filter(username=login).first()
    if user:
        return [user]

    users = list(CofkUser.objects.filter(username__iexact=login))
    if users:
        return users

    return list(CofkUser.objects.filter(email__iexact=login))


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
