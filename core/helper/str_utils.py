import random
import string


def create_random_str(n_char=10):
    s = string.ascii_letters + string.digits
    return ''.join(random.choices(s, k=n_char))


def join_str_list(str_list, drop_empty=True, delimiter=', '):
    if drop_empty:
        str_list = filter(None, str_list)
    str_list = map(str, str_list)
    return delimiter.join(str_list)
