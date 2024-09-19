import functools
import logging
from pathlib import Path

from cllib import inspect_utils
from core import exporter
from core.helper import task_serv
from core.helper.task_serv import FileBaseTaskStatusHandler
from siteedit2.settings import EMLO_APP_HOME

PATH_EXPORTER_OUTPUT = Path(EMLO_APP_HOME).joinpath('exporter')
PATH_EXPORTER_OUTPUT.mkdir(parents=True, exist_ok=True)

log = logging.getLogger(__name__)

status_handler = FileBaseTaskStatusHandler(name='exporter_flag')


def run_exporter():
    run_task_fn = functools.partial(exporter.export_all,
                                    output_dir=PATH_EXPORTER_OUTPUT,
                                    skip_url_check=False)
    task_serv.run_task(run_task_fn, status_handler)


RUN_EXPORTER_FUNC = inspect_utils.get_fn_path(run_exporter)
