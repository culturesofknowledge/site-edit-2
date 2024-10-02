import datetime
import functools

from django.apps import AppConfig

from core.helper import django_q_serv


class ClonefinderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clonefinder'

    def ready(self):
        from django_q.models import Schedule
        from django_q.tasks import schedule
        from clonefinder.services.clonefinder_schedule import RUN_CLONEFINDER_CLUSTERING_FN

        schedule_fn = functools.partial(schedule,
                                        schedule_type=Schedule.MINUTES,
                                        q_options={'timeout': 24 * 60 * 60},
                                        next_run=datetime.datetime.now()
                                        )
        django_q_serv.init_schedule(RUN_CLONEFINDER_CLUSTERING_FN, schedule_fn)
