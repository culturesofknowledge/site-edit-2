"""
Helpers for the user recorded in the audit trail.

The DB audit triggers read the PostgreSQL setting ``app.current_user``. Web requests set it in
``AuditUserMiddleware``; code that runs outside a request (e.g. django-q tasks) must set it itself
with ``set_audit_user``. Audit rows written from Python should use ``get_audit_user`` so they record
the same user as the triggers.
"""
from django.db import connection

from core import constant


def set_audit_user(username: str):
    """Set the audit user for the current transaction only. Call it inside ``transaction.atomic()``."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.current_user', %s, true)", [username or ''])


def get_audit_user(instance=None) -> str:
    """
    Return the user making the current change: the ``app.current_user`` setting if set, else the
    instance's ``change_user``, else ``constant.DEFAULT_CHANGE_USER``.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('app.current_user', true)")
        username = cursor.fetchone()[0]
    return username or getattr(instance, 'change_user', None) or constant.DEFAULT_CHANGE_USER
