from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class CofkSuggestions(models.Model):
    suggestion_id = models.AutoField(primary_key=True)
    suggestion_new = models.BooleanField(default=True)
    suggestion_type = models.CharField(max_length=200)
    suggestion_suggestion = models.TextField()
    # suggestion_relation = models.CharField(max_length=200, default="None")
    # suggestion_related_record = models.ForeignKey('CofkRecords', on_delete=models.CASCADE, null=True, blank=True)
    suggestion_status = models.CharField(max_length=256, default="New")

    # Automatic fields
    suggestion_created_at = models.DateTimeField(auto_now_add=True)
    suggestion_updated_at = models.DateTimeField(auto_now=True)
    suggestion_resolved_at = models.DateTimeField(null=True, blank=True)
    suggestion_author = models.CharField(max_length=256, default="Anonymous")

    # Relation fields for ForeignKey-like feature
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggestion_relation'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    suggestion_related_record = GenericForeignKey('content_type', 'suggestion_id')

    class Meta:
        db_table = 'cofk_union_suggestions'
