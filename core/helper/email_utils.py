import logging
from typing import Iterable

import requests
from django.conf import settings

log = logging.getLogger(__name__)


def send_email(to: str | Iterable[str],
               subject='No subject',
               content='No content',
               attachments=None,
               **kwargs):
    attachments = attachments or []
    if not isinstance(to, str):
        to = map(lambda s: f'<{s}>', to)
        to = ','.join(to)
    else:
        to = f'<{to}>'

    resp = requests.post(
        f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": f"Mailgun Sandbox <postmaster@{settings.MAILGUN_DOMAIN}>",
            "to": to,
            "subject": subject,
            "text": content
        },
        files=[
            ('attachment', name_and_bytes) for name_and_bytes in attachments
        ],
        **kwargs,
    )
    if resp.status_code != 200:
        log.error(f'send mail fail -- [{subject}]')
    return resp
