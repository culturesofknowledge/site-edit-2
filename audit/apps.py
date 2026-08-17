
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
            model_signals.handle_update_recref_date(sender, instance)
            model_signals.handle_update_language_notes(sender, instance)

        def on_post_save(sender: ModelBase, instance: models.Model, created: bool,
                         raw: bool, using, update_fields, **kwargs):
            model_signals.handle_create_recref_date(sender, instance)
            if created:
                model_signals.add_relation_audit_to_literal(sender, instance)
                model_signals.handle_non_triggered_record(sender, instance, is_create=True)
            elif (old_notes := getattr(instance, 'old_notes_for_audit', model_signals._NO_OLD_NOTES)) \
                    is not model_signals._NO_OLD_NOTES:
                model_signals.handle_non_triggered_record(sender, instance, is_create=None, old_notes=old_notes)

        def on_post_delete(sender: ModelBase, instance: models.Model, using, **kwargs):
            model_signals.handle_non_triggered_record(sender, instance, is_create=False)
            model_signals.add_relation_audit_to_literal_on_delete(sender, instance)

        pre_save.connect(on_pre_save, weak=False)
        post_save.connect(on_post_save, weak=False)
        post_delete.connect(on_post_delete, weak=False)
