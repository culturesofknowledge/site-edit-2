from django.apps import AppConfig

from django.db.models.signals import post_save, post_delete


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'

    def ready(self):
        from . import model_signals  # avoid import models before app ready
        post_save.connect(model_signals.on_update_audit_changed_user)
        post_delete.connect(model_signals.on_delete_queryable_work)
