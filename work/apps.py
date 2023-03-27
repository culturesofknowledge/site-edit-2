import logging

from django.apps import AppConfig

log = logging.getLogger(__name__)


class WorkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'work'
