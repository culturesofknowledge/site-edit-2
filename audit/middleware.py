from django.db import connection


class AuditUserMiddleware:
    """
    Sets the PostgreSQL session variable app.current_user so that audit triggers
    can record who made each change without needing a post-save patching step.
    Must be listed after AuthenticationMiddleware in MIDDLEWARE settings.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        username = user.username if (user and user.is_authenticated) else '__unknown_user'
        with connection.cursor() as cursor:
            cursor.execute("SELECT set_config('app.current_user', %s, false)", [username])
        try:
            return self.get_response(request)
        finally:
            with connection.cursor() as cursor:
                cursor.execute("SELECT set_config('app.current_user', '', false)")
