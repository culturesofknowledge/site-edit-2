from django.apps import AppConfig


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in
        from django.utils import timezone
        from login.models import CofkUser

        def update_login_times(sender, request, user, **kwargs):
            user.prev_login = user.login_time
            user.login_time = timezone.now()
            user.save(update_fields=['prev_login', 'login_time'])

        user_logged_in.connect(update_login_times, sender=CofkUser)
