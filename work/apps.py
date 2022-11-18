import logging

from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete

log = logging.getLogger(__name__)


class WorkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'work'

    def ready(self):
        from . import model_signals  # avoid import models before app ready
        post_save.connect(model_signals.on_clone_queryable_work)
        post_delete.connect(model_signals.on_delete_queryable_work)
