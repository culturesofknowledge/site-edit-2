from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.db import OperationalError, ProgrammingError

        from core.helper import exporter_serv
        try:
            exporter_serv.sync_schedules()
        except (OperationalError, ProgrammingError):
            # Table doesn't exist yet - migrations haven't run
            pass
