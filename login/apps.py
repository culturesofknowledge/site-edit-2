from django.apps import AppConfig


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in, user_login_failed
        from django.db.models import F
        from django.utils import timezone
        from login.models import CofkUser

        def update_login_times(sender, request, user, **kwargs):
            user.prev_login = user.login_time
            user.login_time = timezone.now()
            user.save(update_fields=['prev_login', 'login_time'])

        def increment_failed_logins(sender, credentials, request=None, **kwargs):
            # credentials is sanitised (password redacted) but the username
            # field is left as-is. No user instance is available here --
            # the username may not even match a real account -- so update()
            # rather than fetch+save, which is a no-op for an unknown user
            # instead of raising DoesNotExist.
            username = credentials.get('username')
            if username:
                CofkUser.objects.filter(pk=username).update(failed_logins=F('failed_logins') + 1)

        user_logged_in.connect(update_login_times, sender=CofkUser, weak=False)
        # user_login_failed is sent with sender=<module name>, not the user
        # model, so it can't be filtered by sender the way user_logged_in is.
        user_login_failed.connect(increment_failed_logins, weak=False)
