import logging

log = logging.getLogger(__name__)


def init_schedule(fn_name, schedule_fn):
    from django_q.models import Schedule
    try:
        schedule_job_size = Schedule.objects.filter(func=fn_name).count()
        if not schedule_job_size:
            schedule_fn(fn_name)
    except Exception as e:
        log.error('Failed to schedule exporter', exc_info=e)
