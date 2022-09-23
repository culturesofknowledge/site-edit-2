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
    if to == '' or to is None or to == []:
        log.warning('skip send email, [to] should not empty')
        return

    attachments = attachments or []
    if isinstance(to, str):
        to = [to, settings.MAILGUN_DOMAIN]
    else:
        to = list(to)

    log.debug(f'send email -- [{to=}][{settings.MAILGUN_DOMAIN}][{subject}]')

    resp = requests.post(
        f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": f"Excited User <mailgun@{settings.MAILGUN_DOMAIN}>",
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
        log.error(f'send mail fail -- [{resp.text}][{to}][{subject=}][{settings.MAILGUN_DOMAIN}]')
    return resp
