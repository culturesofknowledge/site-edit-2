from django.db import models


class AuditRecrefAdapter:

    def __init__(self, instance: models.Model):
        self.instance = instance

    def key_value_text(self):
        return str(self.instance.pk)

    def key_value_integer(self):
        return self.key_value_text()

    def key_decode(self):
        return f'Empty or missing value in {self.instance._meta.db_table} with key {self.key_value_text()}'
