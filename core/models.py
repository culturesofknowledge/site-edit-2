import uuid

from django.db import models


class CofkUnionComment(models.Model):
    class Meta:
        db_table = 'cofk_union_comment'

    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkUnionRelationshipType(models.Model):
    class Meta:
        db_table = 'cofk_union_relationship_type'

    relationship_code = models.CharField(max_length=50, primary_key=True)
    desc_left_to_right = models.CharField(max_length=200, null=False, default='')
    desc_right_to_left = models.CharField(max_length=200, null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)


class CofkUnionResource(models.Model):
    class Meta:
        db_table = 'cofk_union_resource'

    resource_id = models.AutoField(primary_key=True)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkUnionRelationship(models.Model):
    class Meta:
        db_table = 'cofk_union_relationship'

    relationship_id = models.AutoField(primary_key=True)
    left_table_name = models.CharField(max_length=100, null=False)
    left_id_value = models.CharField(max_length=100, null=False)
    relationship_type = models.ForeignKey(CofkUnionRelationshipType, null=False, on_delete=models.DO_NOTHING)
    right_table_name = models.CharField(max_length=100, null=False)
    right_id_value = models.CharField(max_length=100, null=False)
    relationship_valid_from = models.DateTimeField()
    relationship_valid_till = models.DateTimeField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)
