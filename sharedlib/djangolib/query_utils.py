from typing import Iterable

from django.db.models import TextField
from django.db.models.functions import Concat, Cast


def concat_safe(items: Iterable):
    return Concat(
        *[Cast(f, TextField()) for f in items]
    )
