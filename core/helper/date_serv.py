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


def str_to_std_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, constant.STD_DATE_FORMAT)


def date_to_simple_date_str(dt):
    """
    >>> date_to_simple_date_str(datetime.datetime(2020, 1, 1))
    '20200101'
    """
    return dt.strftime(constant.SIMPLE_DATE_FORMAT)


calendar_choices = [
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
