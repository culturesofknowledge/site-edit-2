import logging
from pathlib import Path

from django_q.models import Schedule
from django_q.tasks import schedule

from core import exporter
from siteedit2.settings import EMLO_APP_HOME

PATH_EXPORTER_OUTPUT = Path(EMLO_APP_HOME).joinpath('exporter')

log = logging.getLogger(__name__)

RUN_EXPORTER_FUNC = 'core.helper.exporter_serv.run_exporter'


def is_exporter_pending() -> bool:
    return Schedule.objects.filter(func=RUN_EXPORTER_FUNC).count()


def mark_exporter_pending():
    if not is_exporter_pending():
        schedule(
            RUN_EXPORTER_FUNC,
            schedule_type=Schedule.DAILY,
            hours=0,
            # schedule_type=Schedule.MINUTES,
            # minutes=1,
            q_options={'timeout': 12 * 60 * 60, },
        )


def run_exporter():
    log.info('Exporter triggered')
    exporter.export_all(output_dir=PATH_EXPORTER_OUTPUT, skip_url_check=False)
    log.info('Exporter done')
