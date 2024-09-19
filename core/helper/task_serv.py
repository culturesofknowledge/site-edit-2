import logging
from pathlib import Path
from typing import Callable

from siteedit2.settings import EMLO_APP_HOME

log = logging.getLogger(__name__)


class FileBaseTaskStatusHandler:
    ST_DONE = '0'
    ST_PENDING = '1'
    ST_RUNNING = '2'

    def __init__(self, path=None, name=None):
        if path is None and name is None:
            raise ValueError('Either path or name must be provided')

        self.path = path
        if self.path is None:
            self.path = Path(EMLO_APP_HOME).joinpath('task_status_handler').joinpath(name)

        self.path.parent.mkdir(parents=True, exist_ok=True)

    def is_pending(self) -> bool:
        return self.path.is_file() and self.path.read_text().strip() == self.ST_PENDING

    def is_running(self) -> bool:
        return self.path.is_file() and self.path.read_text().strip() == self.ST_RUNNING

    def is_done(self) -> bool:
        return self.path.is_file() and self.path.read_text().strip() == self.ST_DONE

    def is_pending_or_running(self) -> bool:
        return self.is_pending() or self.is_running()

    def mark_pending(self):
        """ Mark the task as pending if task needs to be run """
        self.path.write_text(self.ST_PENDING)

    def mark_running(self):
        self.path.write_text(self.ST_RUNNING)

    def mark_done(self):
        self.path.write_text(self.ST_DONE)


def run_task(run_task_fn: Callable[[], None],
             status_handler: FileBaseTaskStatusHandler):
    if not status_handler.is_pending():
        log.info('Task not pending')
        return

    status_handler.mark_running()
    log.info('Task triggered')
    try:
        run_task_fn()
        log.info('Task done')
    except Exception as e:
        log.error('Task failed', exc_info=e)

    status_handler.mark_done()
