import random
import string


def create_random_str(n_char=10):
    s = string.ascii_letters + string.digits
    return ''.join(random.choices(s, k=n_char))
