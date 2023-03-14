from typing import Iterable, Any


def join_csv_value_common(values: Iterable[Any]) -> str:
    values = map(str, values)
    return ' ~ '.join(values)


def join_comment_lines(comments: Iterable) -> str:
    return join_csv_value_common((r.comment for r in comments))


def join_image_lines(images: Iterable) -> str:
    return join_csv_value_common((r.image_filename for r in images))
