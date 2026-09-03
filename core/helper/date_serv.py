import datetime

from core import constant


def str_to_search_datetime(datetime_str):
    """
    >>> str_to_search_datetime('2020')
    datetime.datetime(2020, 1, 1, 0, 0)
    >>> str_to_search_datetime('2020-12-22')

    >>> str_to_search_datetime('22/12/2020')
    datetime.datetime(2020, 12, 22, 0, 0)
    """

    if len(datetime_str) == 4:
        datetime_str = f'01/01/{datetime_str}'
    elif len(datetime_str) == 7:
        datetime_str = f'01/{datetime_str}'

    _format = constant.SEARCH_DATETIME_FORMAT if len(datetime_str) > 10 else constant.SEARCH_DATE_FORMAT

    try:
        return datetime.datetime.strptime(datetime_str, _format)
    except ValueError:
        pass


def search_datestr_to_db_datestr(date_str: str) -> str:
    """
    >>> search_datestr_to_db_datestr('31/12/2020')
    '2020-12-31'
    >>> search_datestr_to_db_datestr('2020')
    '2020-01-01'
    """

    if not date_str:
        return date_str
    dates = date_str.split('/')
    day = month = '01'
    if len(dates) == 1:
        year = dates[0]
    elif len(dates) == 2:
        month, year = dates
    else:
        day, month, year = dates[:3]
    return f'{year}-{month}-{day}'


def search_datestr_to_db_datestr_end(date_str: str) -> str:
    """
    Convert a search date string to a DB date string, but if only a year or month/year
    are provided, use the last day of the period (31/12 for year-only, last day of month for mm/yyyy).

    Examples
    --------
    >>> search_datestr_to_db_datestr_end('2020')
    '2020-12-31'
    >>> search_datestr_to_db_datestr_end('02/2020')
    '2020-02-29'
    >>> search_datestr_to_db_datestr_end('15/03/2020')
    '2020-03-15'
    """

    if not date_str:
        return date_str

    parts = date_str.split('/')
    # Year only
    if len(parts) == 1:
        year = int(parts[0])
        return f'{year:04d}-12-31'
    # Month/Year
    if len(parts) == 2:
        month = int(parts[0])
        year = int(parts[1])
        # compute last day of month by rolling to next month day 1 then subtracting a day
        if month == 12:
            next_month = datetime.date(year + 1, 1, 1)
        else:
            next_month = datetime.date(year, month + 1, 1)
        last_day = next_month - datetime.timedelta(days=1)
        return last_day.strftime('%Y-%m-%d')

    # Full date provided: keep as-is but convert order
    day, month, year = parts[:3]
    return f'{int(year):04d}-{int(month):02d}-{int(day):02d}'


def normalize_search_display_start(date_str: str) -> str:
    """
    Normalize a search input string for displaying the start of a range.
    Year-only -> 01/01/YYYY; MM/YYYY -> 01/MM/YYYY; DD/MM/YYYY -> unchanged.
    """
    if not date_str:
        return date_str
    parts = date_str.split('/')
    if len(parts) == 1:
        return f'01/01/{parts[0]}'
    if len(parts) == 2:
        return f'01/{parts[0].zfill(2)}/{parts[1]}'
    # Ensure zero-padded
    d, m, y = parts[:3]
    return f'{int(d):02d}/{int(m):02d}/{y}'


def normalize_search_display_end(date_str: str) -> str:
    """
    Normalize a search input string for displaying the end of a range.
    Year-only -> 31/12/YYYY; MM/YYYY -> <last-day>/MM/YYYY; DD/MM/YYYY -> unchanged.
    """
    if not date_str:
        return date_str
    parts = date_str.split('/')
    if len(parts) == 1:
        return f'31/12/{parts[0]}'
    if len(parts) == 2:
        month = int(parts[0])
        year = int(parts[1])
        if month == 12:
            next_month = datetime.date(year + 1, 1, 1)
        else:
            next_month = datetime.date(year, month + 1, 1)
        last_day = (next_month - datetime.timedelta(days=1)).day
        return f'{last_day:02d}/{month:02d}/{year}'
    # Full date provided
    d, m, y = parts[:3]
    return f'{int(d):02d}/{int(m):02d}/{y}'


def str_to_std_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, constant.STD_DATE_FORMAT)


def date_to_simple_date_str(dt):
    """
    >>> date_to_simple_date_str(datetime.datetime(2020, 1, 1))
    '20200101'
    """
    return dt.strftime(constant.SIMPLE_DATE_FORMAT)


def validate_search_date_str(date_str: str) -> str | None:
    """
    Validate a search date string in dd/mm/yyyy, mm/yyyy, or yyyy format.
    Returns an error message if invalid, or None if valid.
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()
    parts = date_str.split('/')

    try:
        if len(parts) == 1:
            year = int(parts[0])
            if year < 1 or year > 9999:
                return 'Invalid date format. Please use dd/mm/yyyy, mm/yyyy, or yyyy.'
        elif len(parts) == 2:
            month, year = int(parts[0]), int(parts[1])
            if not (1 <= month <= 12) or year < 1 or year > 9999:
                return 'Invalid date format. Please use dd/mm/yyyy, mm/yyyy, or yyyy.'
        elif len(parts) == 3:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 1 or year > 9999:
                return 'Invalid date format. Please use dd/mm/yyyy, mm/yyyy, or yyyy.'
            # Validate the actual date
            datetime.date(year, month, day)
        else:
            return 'Invalid date format. Please use dd/mm/yyyy, mm/yyyy, or yyyy.'
    except (ValueError, TypeError):
        return 'Invalid date format. Please use dd/mm/yyyy, mm/yyyy, or yyyy.'

    return None


calendar_choices = [
    ('', 'Unknown'),
    ('G', 'Gregorian'),
    ('JJ', 'Julian (year starting 1st Jan)'),
    ('JM', 'Julian (year starting 25th Mar) (Please only use this option after consultation with EMLO\'s editors)'),
    ('O', 'Other'),
]

calendar_choices_person = [
    ('', 'Unknown'),
    ('G', 'Gregorian'),
    ('JJ', 'Julian (year starting 1st Jan)'),
    ('JM', 'Julian (year starting 25th Mar)'),
    ('O', 'Other'),
]


def decode_calendar(calendar_code, default='Unknown') -> str:
    for code, name in calendar_choices:
        if code == calendar_code:
            return name
    return default
