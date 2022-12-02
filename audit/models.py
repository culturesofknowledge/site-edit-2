from django.db import models

from core.helper import model_utils


class CofkUnionAuditLiteral(models.Model):
    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50, null=False)
    change_type = models.CharField(max_length=3, null=False)
    table_name = models.CharField(max_length=100, null=False)
    key_value_text = models.CharField(max_length=100, null=False)
    key_value_integer = models.IntegerField(blank=True, null=True)
    key_decode = models.TextField(blank=True, null=True)
    column_name = models.CharField(max_length=100, null=False)
    new_column_value = models.TextField(blank=True, null=True)
    old_column_value = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_audit_literal'


class CofkUnionAuditRelationship(models.Model):
    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    change_type = models.CharField(max_length=3)
    left_table_name = models.CharField(max_length=100)
    left_id_value_new = models.CharField(max_length=100)
    left_id_decode_new = models.TextField()
    left_id_value_old = models.CharField(max_length=100)
    left_id_decode_old = models.TextField()
    relationship_type = models.CharField(max_length=100)
    relationship_decode_left_to_right = models.CharField(max_length=100)
    relationship_decode_right_to_left = models.CharField(max_length=100)
    right_table_name = models.CharField(max_length=100)
    right_id_value_new = models.CharField(max_length=100)
    right_id_decode_new = models.TextField()
    right_id_value_old = models.CharField(max_length=100)
    right_id_decode_old = models.TextField()

    class Meta:
        db_table = 'cofk_union_audit_relationship'
