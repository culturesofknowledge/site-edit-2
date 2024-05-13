import logging
from pathlib import Path

from core import exporter
from siteedit2.settings import EMLO_APP_HOME

PATH_EXPORTER_OUTPUT = Path(EMLO_APP_HOME).joinpath('exporter')
PATH_EXPORTER_OUTPUT.mkdir(parents=True, exist_ok=True)
PATH_EXPORTER_FLAG = Path(EMLO_APP_HOME) / 'exporter_flag'

log = logging.getLogger(__name__)

RUN_EXPORTER_FUNC = 'core.helper.exporter_serv.run_exporter'
ST_DONE = '0'
ST_PENDING = '1'
ST_RUNNING = '2'


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
