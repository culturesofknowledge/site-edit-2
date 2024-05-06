import logging
from pathlib import Path

from django_q.models import Schedule
from django_q.tasks import schedule

from siteedit2.settings import EMLO_APP_HOME

PATH_EXPORTER_FLAG = Path(EMLO_APP_HOME).joinpath('exporter_flag')

log = logging.getLogger(__name__)

RUN_EXPORTER_FUNC = 'core.helper.exporter_serv.run_exporter'


def is_exporter_pending() -> bool:
    return Schedule.objects.filter(func=RUN_EXPORTER_FUNC).count()


def mark_exporter_pending():
    if not is_exporter_pending():
        schedule(
            RUN_EXPORTER_FUNC,
            schedule_type=Schedule.ONCE,
            minutes=1,
            q_options={'timeout': 600, },
        )


def run_exporter():
    log.info('Exporter triggered')
    print('akldjalksdjlakjdlkasjdlkasjdlk')
