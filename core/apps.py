import datetime

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django_q.models import Schedule

        from core.helper.exporter_serv import RUN_EXPORTER_FUNC
        if not Schedule.objects.filter(func=RUN_EXPORTER_FUNC).count():
            from django_q.tasks import schedule
            schedule(
                RUN_EXPORTER_FUNC,
                schedule_type=Schedule.DAILY,
                # schedule_type=Schedule.MINUTES,
                # minutes=1,
                q_options={'timeout': 24 * 60 * 60},

                next_run=(datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0,
                                                                                        second=0, microsecond=0),
                # next_run=datetime.datetime.now(),
            )
