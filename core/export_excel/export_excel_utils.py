from collections.abc import Iterable

from core.models import CofkUnionComment


def notes(note_list: Iterable[CofkUnionComment]) -> str:
    comments = (n.comment for n in note_list)
    comments = filter(None, comments)
    return '; '.join(comments)



