import datetime

from core import constant


def str_to_search_datetime(datetime_str):
    if len(datetime_str) == 4:
        datetime_str = f'01/01/{datetime_str}'
    elif len(datetime_str) == 7:
        datetime_str = f'01/{datetime_str}'

    _format = constant.SEARCH_DATETIME_FORMAT if len(datetime_str) > 10 else constant.SEARCH_DATE_FORMAT

    try:
        return datetime.datetime.strptime(datetime_str, _format)
    except ValueError:
        pass

def str_to_std_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, constant.STD_DATE_FORMAT)


def date_to_simple_date_str(dt):
    return dt.strftime(constant.SIMPLE_DATE_FORMAT)
