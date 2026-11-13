"""
Scheduled exports for the EMLO front end.

Three kinds of run write the CSV files into PATH_EXPORTER_OUTPUT, followed by
a `need_index` file ("0" or "1") telling whoever copies the files to the front end
whether the front end SOLR needs re-indexing:

* regular   -- recurring, every EXPORTER_SCHEDULE_TYPE on EXPORTER_SCHEDULE_WEEKDAYS,
               need_index=0 (unless an indexing export has been requested, see below)
* weekly    -- every week on EXPORTER_INDEX_WEEKDAY, need_index=1
* requested -- one-off, queued for the next regular run time when a user
               clicks Export on the dashboard, need_index=1

A request is a marker file (PATH_INDEX_REQUESTED), so whichever run starts first after the click serves it and it is
never lost: it survives a busy or failed run. Only one export runs at a time
(PATH_EXPORTER_LOCK); a run that finds another export in progress skips, and
an indexing run that would be skipped is re-queued instead.
"""
import datetime
import fcntl
import logging
import os
from contextlib import contextmanager
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from core import exporter
from siteedit2.settings import EMLO_APP_HOME

PATH_EXPORTER_OUTPUT = Path(EMLO_APP_HOME).joinpath('exporter')
PATH_EXPORTER_OUTPUT.mkdir(parents=True, exist_ok=True)
PATH_NEED_INDEX = PATH_EXPORTER_OUTPUT / 'need_index'

PATH_EXPORTER_LOCK = Path(EMLO_APP_HOME) / 'exporter.lock'
# an indexing export has been requested and not started yet
PATH_INDEX_REQUESTED = Path(EMLO_APP_HOME) / 'exporter_index_requested'
# an indexing export is running (left behind if that run was killed)
PATH_INDEX_IN_PROGRESS = Path(EMLO_APP_HOME) / 'exporter_index_in_progress'

log = logging.getLogger(__name__)

RUN_REGULAR_EXPORT_FUNC = 'core.helper.exporter_serv.run_regular_export'
RUN_WEEKLY_INDEX_EXPORT_FUNC = 'core.helper.exporter_serv.run_weekly_index_export'
RUN_REQUESTED_EXPORT_FUNC = 'core.helper.exporter_serv.run_requested_export'

SCHEDULE_NAME_REGULAR = 'exporter_regular'
SCHEDULE_NAME_WEEKLY_INDEX = 'exporter_weekly_index'
SCHEDULE_NAME_REQUESTED = 'exporter_requested'

EXPORT_TASK_TIMEOUT = 24 * 60 * 60
# how long a requested/weekly run waits before retrying when another export is running
BUSY_RETRY_DELAY = datetime.timedelta(minutes=30)

# schedule types that start at EXPORTER_SCHEDULE_TIME and keep that time of day,
# the others (minutes, hourly) start one interval after startup
TIME_ANCHORED_SCHEDULE_TYPES = {'D', 'W', 'BW', 'M', 'BM', 'Q', 'Y'}


class ExporterBusy(Exception):
    pass


# ---------------------------------------------------------------------------
# config

def _parse_time(name: str, default: str) -> datetime.time:
    value = getattr(settings, name, default)
    try:
        return datetime.datetime.strptime(value, '%H:%M').time()
    except (TypeError, ValueError):
        raise ImproperlyConfigured(f'{name} must be a "HH:MM" string, got {value!r}') from None


def get_schedule_type() -> str:
    from django_q.models import Schedule
    schedule_type = getattr(settings, 'EXPORTER_SCHEDULE_TYPE', Schedule.DAILY)
    valid = {t for t, _ in Schedule.TYPE} - {Schedule.ONCE, Schedule.CRON}
    if schedule_type not in valid:
        raise ImproperlyConfigured(f'EXPORTER_SCHEDULE_TYPE must be one of {sorted(valid)}, got {schedule_type!r}')
    return schedule_type


def get_schedule_minutes() -> int | None:
    minutes = getattr(settings, 'EXPORTER_SCHEDULE_MINUTES', None)
    if get_schedule_type() == 'I' and not (isinstance(minutes, int) and minutes > 0):
        raise ImproperlyConfigured(
            'EXPORTER_SCHEDULE_MINUTES must be a positive int when EXPORTER_SCHEDULE_TYPE is "I"')
    return minutes


def get_schedule_time() -> datetime.time:
    return _parse_time('EXPORTER_SCHEDULE_TIME', '00:00')


def get_schedule_weekdays() -> set[int]:
    weekdays = getattr(settings, 'EXPORTER_SCHEDULE_WEEKDAYS', range(7))
    if (isinstance(weekdays, str) or not hasattr(weekdays, '__iter__')
            or not weekdays or any(d not in range(7) for d in weekdays)):
        raise ImproperlyConfigured(
            f'EXPORTER_SCHEDULE_WEEKDAYS must be a non-empty list of 0 (Monday) to 6 (Sunday), got {weekdays!r}')
    return set(weekdays)


def get_index_weekday() -> int:
    weekday = getattr(settings, 'EXPORTER_INDEX_WEEKDAY', 6)
    if weekday not in range(7):
        raise ImproperlyConfigured(f'EXPORTER_INDEX_WEEKDAY must be 0 (Monday) to 6 (Sunday), got {weekday!r}')
    return weekday


def get_index_time() -> datetime.time:
    return _parse_time('EXPORTER_INDEX_TIME', '04:00')


def first_regular_run(schedule_type: str, minutes: int | None,
                      now: datetime.datetime = None) -> datetime.datetime:
    now = now or datetime.datetime.now()
    schedule_time = get_schedule_time()  # validated for every type, request_export() may use it
    if schedule_type in TIME_ANCHORED_SCHEDULE_TYPES:
        return next_time_of_day(schedule_time, now)
    return now + datetime.timedelta(minutes=minutes if schedule_type == 'I' else 60)


def next_time_of_day(time_of_day: datetime.time, now: datetime.datetime = None) -> datetime.datetime:
    now = now or datetime.datetime.now()
    next_run = datetime.datetime.combine(now.date(), time_of_day)
    if next_run <= now:
        next_run += datetime.timedelta(days=1)
    return next_run


def next_weekday_time(weekday: int, time_of_day: datetime.time,
                      now: datetime.datetime = None) -> datetime.datetime:
    now = now or datetime.datetime.now()
    next_run = datetime.datetime.combine(now.date(), time_of_day)
    next_run += datetime.timedelta(days=(weekday - now.weekday()) % 7)
    if next_run <= now:
        next_run += datetime.timedelta(days=7)
    return next_run


# ---------------------------------------------------------------------------
# state

def is_exporter_pending() -> bool:
    """True while an indexing export has been requested or is running -- for
    the "Exporter is pending..." message on the dashboard."""
    return PATH_INDEX_REQUESTED.is_file() or PATH_INDEX_IN_PROGRESS.is_file()


def _request_index():
    PATH_INDEX_REQUESTED.touch()


def _claim_index_request() -> bool:
    """Take over a pending request (atomically, so a click arriving now is
    either taken by this run or left for the next one). A leftover
    in-progress marker means an indexing run was killed -- redo it."""
    try:
        os.replace(PATH_INDEX_REQUESTED, PATH_INDEX_IN_PROGRESS)
        return True
    except FileNotFoundError:
        return PATH_INDEX_IN_PROGRESS.is_file()


def write_need_index(needs_index: bool):
    tmp_path = PATH_NEED_INDEX.with_name(PATH_NEED_INDEX.name + '.tmp')
    tmp_path.write_text('1\n' if needs_index else '0\n')
    tmp_path.replace(PATH_NEED_INDEX)


@contextmanager
def _exporter_lock():
    # flock is released by the OS if the worker dies, so it never goes stale
    with open(PATH_EXPORTER_LOCK, 'a', encoding='utf-8') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ExporterBusy() from exc
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# runs

def _export(needs_index: bool, only_if_requested: bool = False):
    try:
        with _exporter_lock():
            requested = _claim_index_request()
            if only_if_requested and not requested:
                log.info('Exporter skipped, requested export was already done by another run')
                return
            needs_index = needs_index or requested
            if needs_index:
                PATH_INDEX_IN_PROGRESS.touch()

            log.info(f'Exporter triggered, need_index={int(needs_index)}')
            try:
                exporter.export_all(output_dir=PATH_EXPORTER_OUTPUT, clear_output_dir=True,
                                    skip_url_check=getattr(settings, 'EXPORTER_SKIP_URL_CHECK', False))
                write_need_index(needs_index)
            except Exception:
                log.exception('Exporter failed')
                if needs_index:
                    # keep the request so the next run retries the indexing export
                    os.replace(PATH_INDEX_IN_PROGRESS, PATH_INDEX_REQUESTED)
                raise
            PATH_INDEX_IN_PROGRESS.unlink(missing_ok=True)
            log.info('Exporter done')
    except ExporterBusy:
        # also hit when django-q redelivers a long running export task
        if not needs_index:
            log.info('Exporter skipped, another export is running')
        elif PATH_INDEX_IN_PROGRESS.is_file():
            log.info('Exporter skipped, an indexing export is already running')
        else:
            log.info(f'Exporter busy, indexing export re-queued in {BUSY_RETRY_DELAY}')
            _request_index()
            schedule_requested_export(datetime.datetime.now() + BUSY_RETRY_DELAY)


def run_regular_export(intended_date: str = None):
    # the day of the scheduled run, not of when a worker picked it up
    run_date = datetime.datetime.fromisoformat(intended_date) if intended_date else datetime.datetime.now()
    if run_date.weekday() not in get_schedule_weekdays():
        log.info(f'Regular export skipped, {run_date:%A} is not in EXPORTER_SCHEDULE_WEEKDAYS')
        return
    _export(needs_index=False)


def run_weekly_index_export():
    _export(needs_index=True)


def run_requested_export():
    """The one-off run queued by request_export()."""
    _export(needs_index=True, only_if_requested=True)


# ---------------------------------------------------------------------------
# scheduling

def schedule_requested_export(next_run: datetime.datetime):
    from django_q.models import Schedule
    from django_q.tasks import schedule
    existing = Schedule.objects.filter(name=SCHEDULE_NAME_REQUESTED).first()
    if existing is None:
        schedule(
            RUN_REQUESTED_EXPORT_FUNC,
            name=SCHEDULE_NAME_REQUESTED,
            schedule_type=Schedule.ONCE,
            q_options={'timeout': EXPORT_TASK_TIMEOUT},
            next_run=next_run,
        )
    elif existing.next_run > next_run:
        existing.next_run = next_run
        existing.save()


def request_export():
    """Called when a user clicks Export on the dashboard: queue an indexing
    export for the next regular run time."""
    from django_q.models import Schedule
    _request_index()
    regular = Schedule.objects.filter(name=SCHEDULE_NAME_REGULAR).first()
    next_run = regular.next_run if regular else next_time_of_day(get_schedule_time())
    schedule_requested_export(max(next_run, datetime.datetime.now()))


def _sync_schedule(name: str, func: str, schedule_type: str, first_run: datetime.datetime,
                   minutes: int | None = None, intended_date_kwarg: str = None):
    from django_q.models import Schedule
    from django_q.tasks import schedule
    existing = Schedule.objects.filter(name=name).first()
    if existing is None:
        schedule(
            func,
            name=name,
            schedule_type=schedule_type,
            minutes=minutes,
            q_options={'timeout': EXPORT_TASK_TIMEOUT},
            next_run=first_run,
            intended_date_kwarg=intended_date_kwarg,
        )
        return

    # restart the schedule from first_run if its config has changed
    changed = (existing.func != func
               or existing.schedule_type != schedule_type
               or existing.minutes != minutes)
    if schedule_type in TIME_ANCHORED_SCHEDULE_TYPES:
        changed = changed or existing.next_run.time() != first_run.time()
    else:
        # first_run is one interval from now, a later next_run is stale
        changed = changed or existing.next_run > first_run
    if schedule_type == Schedule.WEEKLY:
        changed = changed or existing.next_run.weekday() != first_run.weekday()
    if changed:
        existing.func = func
        existing.schedule_type = schedule_type
        existing.minutes = minutes
        existing.next_run = first_run
    if changed or existing.intended_date_kwarg != intended_date_kwarg:
        existing.intended_date_kwarg = intended_date_kwarg
        existing.save()


def sync_schedules():
    """Create or update the recurring export schedules from settings; run on
    every startup so a settings change takes effect after a restart."""
    from django_q.models import Schedule
    schedule_type = get_schedule_type()
    minutes = get_schedule_minutes()
    _sync_schedule(
        SCHEDULE_NAME_REGULAR, RUN_REGULAR_EXPORT_FUNC,
        schedule_type=schedule_type,
        minutes=minutes,
        first_run=first_regular_run(schedule_type, minutes),
        intended_date_kwarg='intended_date',
    )
    get_schedule_weekdays()  # check the setting at startup, it's read by run_regular_export()
    _sync_schedule(
        SCHEDULE_NAME_WEEKLY_INDEX, RUN_WEEKLY_INDEX_EXPORT_FUNC,
        schedule_type=Schedule.WEEKLY,
        first_run=next_weekday_time(get_index_weekday(), get_index_time()),
    )
