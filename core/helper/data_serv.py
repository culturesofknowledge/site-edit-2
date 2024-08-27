import re
from typing import Iterable

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')
def check_test_general_true(value):
    return value == '1' or value == 1 or value is True


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
