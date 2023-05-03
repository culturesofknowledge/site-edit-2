from login.models import CofkUser


def create_test_user(username, raw_password='pass', is_save=True) -> CofkUser:
    login_user = CofkUser()
    login_user.username = username
    if raw_password:
        login_user.raw_password = raw_password
        login_user.set_password(login_user.raw_password)
    if is_save:
        login_user.save()
    return login_user


def create_test_user__a() -> CofkUser:
    user = create_test_user('test_user_a', raw_password='pass', is_save=False)
    user.is_superuser = True
    user.save()
    return user
