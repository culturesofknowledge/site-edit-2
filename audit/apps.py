from django.apps import AppConfig
from django.db import models
from django.db.models.base import ModelBase

from django.db.models.signals import post_save, post_delete, pre_save


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'

    def ready(self):
        from . import model_signals  # avoid import models before app ready

        def on_pre_save(sender: ModelBase, instance: models.Model,
                        raw: bool, using, update_fields, **kwargs):
            model_signals.handle_update_relation_date(sender, instance)

        def on_post_save(sender: ModelBase, instance: models.Model, created: bool,
                         raw: bool, using, update_fields, **kwargs):
            model_signals.handle_create_relation_date(sender, instance)
            model_signals.handle_update_audit_changed_user(sender, instance)
            model_signals.add_relation_audit_to_literal(sender, instance)

        def on_post_delete(sender: ModelBase, instance: models.Model, using, **kwargs):
            model_signals.handle_update_audit_changed_user(sender, instance)

        pre_save.connect(on_pre_save)
        post_save.connect(on_post_save)
        post_delete.connect(on_post_delete)
