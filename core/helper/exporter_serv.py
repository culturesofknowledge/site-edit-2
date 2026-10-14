import datetime
import logging
from pathlib import Path

from core import exporter
from siteedit2.settings import EMLO_APP_HOME

PATH_EXPORTER_OUTPUT = Path(EMLO_APP_HOME).joinpath('exporter')
PATH_EXPORTER_OUTPUT.mkdir(parents=True, exist_ok=True)
PATH_EXPORTER_FLAG = Path(EMLO_APP_HOME) / 'exporter_flag'

log = logging.getLogger(__name__)

RUN_EXPORTER_FUNC = 'core.helper.exporter_serv.run_exporter'
RUN_SCHEDULED_EXPORTER_FUNC = 'core.helper.exporter_serv.run_scheduled_exporter'
ST_DONE = '0'
ST_PENDING = '1'
ST_RUNNING = '2'


def next_midnight() -> datetime.datetime:
    return (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0)


def is_exporter_pending() -> bool:
    return PATH_EXPORTER_FLAG.is_file() and PATH_EXPORTER_FLAG.read_text().strip() == ST_PENDING


def mark_exporter_pending():
    PATH_EXPORTER_FLAG.write_text(ST_PENDING)


def mark_exporter_running():
    PATH_EXPORTER_FLAG.write_text(ST_RUNNING)


def mark_exporter_done():
    PATH_EXPORTER_FLAG.write_text(ST_DONE)


def run_exporter():
    if not is_exporter_pending():
        log.info('Exporter not pending')
        return

    mark_exporter_running()
    log.info('Exporter triggered')
    try:
        exporter.export_all(output_dir=PATH_EXPORTER_OUTPUT, skip_url_check=False)
        log.info('Exporter done')
    except Exception as e:
        log.error('Exporter failed', exc_info=e)

    mark_exporter_done()


def run_scheduled_exporter():
    """Called by the recurring (e.g. weekly) schedule -- runs unconditionally,
    regardless of whether anyone has requested an export via the dashboard."""
    mark_exporter_pending()
    run_exporter()


def trigger_export_tonight():
    """Called when a user requests an export from the dashboard. Marks it
    pending (for the "Exporter is pending..." UI) and queues a one-off run for
    tonight, independent of the recurring schedule's own timer."""
    mark_exporter_pending()

    from django_q.models import Schedule
    from django_q.tasks import schedule
    schedule(
        RUN_EXPORTER_FUNC,
        schedule_type=Schedule.ONCE,
        q_options={'timeout': 24 * 60 * 60},
        next_run=next_midnight(),
    )
