import logging
from pathlib import Path
from typing import Iterable

from django.conf import settings
from django.core.mail import EmailMessage

log = logging.getLogger(__name__)



def send_email(to: str | Iterable[str],
               subject='No subject',
               content='No content',
               attachment_paths: list[str | Path] = None,
               attach_args: Iterable[tuple] = None,
               **kwargs):
    if isinstance(to, str):
        to = [to]
    else:
        to = list(to)

    email = EmailMessage(subject=subject, body=content,
                         from_email=settings.EMAIL_FROM_EMAIL,
                         to=to,
                         **kwargs)

    if attachment_paths:
        for p in attachment_paths:
            email.attach_file(Path(p).as_posix())

    if attach_args:
        for att_data in attach_args:
            if len(att_data) == 2:
                att_name, att_content = att_data
                att_type = None
            else:
                att_name, att_content, att_type = att_data
            email.attach(filename=att_name, content=att_content, mimetype=att_type)

    return email.send()
