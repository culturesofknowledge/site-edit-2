import functools
import logging


def log_no_url(fn):
    @functools.wraps(fn)
    def _wrap(*args, **kwargs):
        url = fn(*args, **kwargs)
        if url is None:
            logging.warning(f'{fn.__name__} failed, person not found [{args}]')
            return ''

        return url

    return _wrap
