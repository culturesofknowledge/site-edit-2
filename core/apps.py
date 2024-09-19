import datetime
import functools
import logging

from django.apps import AppConfig

from core.helper import django_q_serv

log = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django_q.models import Schedule
        from core.helper.exporter_serv import RUN_EXPORTER_FUNC
        from django_q.tasks import schedule

        schedule_fn = functools.partial(schedule, schedule_type=Schedule.DAILY,
                                        q_options={'timeout': 24 * 60 * 60},
                                        next_run=(datetime.datetime.now() + datetime.timedelta(days=1)).replace(
                                            hour=0, minute=0, second=0, microsecond=0))
        django_q_serv.init_schedule(RUN_EXPORTER_FUNC, schedule_fn)
