import re
from typing import Iterable
from urllib.parse import urlsplit

from django.utils.html import format_html

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')
def check_test_general_true(value):
    return value == '1' or value == 1 or value is True


SAFE_URL_SCHEMES = {'', 'http', 'https', 'mailto'}


def is_safe_url(url: str) -> bool:
    """
    True if url is relative or uses a harmless scheme -- rejects e.g. javascript: and data: URLs.
    Browsers ignore whitespace and control characters inside the scheme, so strip those before checking.
    """
    cleaned = re.sub(r'[\x00-\x20\x7f]', '', str(url or ''))
    try:
        return urlsplit(cleaned).scheme.lower() in SAFE_URL_SCHEMES
    except ValueError:
        return False


def render_link(url, text, target='_blank'):
    """ Build an escaped <a> tag; unsafe urls are rendered as plain text """
    if not is_safe_url(url):
        return format_html('{}', text)
    return format_html('<a href="{}" target="{}">{}</a>', url, target, text)


def endcode_url_content(url, text):
    """
    Special encode for url and text content
    """
    return f'xxxCofkLinkStartxxxxxxCofkHrefStartxxx{url}xxxCofkHrefEndxxx{text}xxxCofkLinkEndxxx'


def decode_multi_url_content(encoded) -> Iterable[tuple[str, str]]:
    """
    Special decode for url and text content
    """

    results = re.findall(link_pattern, encoded)
    html = ''

    for result in results:
        yield result[2], result[4]
