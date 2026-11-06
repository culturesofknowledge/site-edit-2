import ast

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.db import OperationalError, ProgrammingError
        from django_q.models import Schedule
        from django.conf import settings

        from core.helper.exporter_serv import (RUN_EXPORTER_FUNC, RUN_SCHEDULED_EXPORTER_FUNC, exporter_q_options,
                                               next_midnight)
        schedule_type = getattr(settings, 'EXPORTER_SCHEDULE_TYPE', Schedule.WEEKLY)
        try:
            # the recurring export used to run RUN_EXPORTER_FUNC directly (gated on the
            # pending flag); it now runs RUN_SCHEDULED_EXPORTER_FUNC (unconditional) --
            # migrate an existing schedule row in place rather than leaving it orphaned.
            existing = Schedule.objects.filter(func__in=[RUN_EXPORTER_FUNC, RUN_SCHEDULED_EXPORTER_FUNC]).first()
            if existing is None:
                from django_q.tasks import schedule
                schedule(
                    RUN_SCHEDULED_EXPORTER_FUNC,
                    schedule_type=schedule_type,
                    q_options=exporter_q_options(),
                    next_run=next_midnight(),
                )
            else:
                # Schedule.kwargs is stored as a dict literal string (see django_q.scheduler)
                try:
                    kwargs = ast.literal_eval(existing.kwargs) if existing.kwargs else {}
                except (ValueError, SyntaxError):
                    kwargs = {}
                # also refresh q_options: rows created earlier carry a 24h timeout, longer
                # than Q_CLUSTER['retry'], which made the ORM broker re-run the export
                if (existing.func != RUN_SCHEDULED_EXPORTER_FUNC or existing.schedule_type != schedule_type
                        or kwargs.get('q_options') != exporter_q_options()):
                    existing.func = RUN_SCHEDULED_EXPORTER_FUNC
                    existing.schedule_type = schedule_type
                    existing.kwargs = str({**kwargs, 'q_options': exporter_q_options()})
                    existing.save()
        except (OperationalError, ProgrammingError):
            # Table doesn't exist yet - migrations haven't run
            pass