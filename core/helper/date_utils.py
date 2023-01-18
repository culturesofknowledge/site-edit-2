import datetime

from core import constant


def str_to_search_datetime(datetime_str):
    _format = constant.SEARCH_DATETIME_FORMAT if len(datetime_str) > 10 else constant.SEARCH_DATE_FORMAT
    return datetime.datetime.strptime(datetime_str, _format)


def str_to_std_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, constant.STD_DATE_FORMAT)