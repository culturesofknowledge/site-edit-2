from django.db import models

from core.helper import model_utils


class CofkUnionPublication(models.Model):
    publication_id = models.AutoField(primary_key=True)
    publication_details = models.TextField()
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=50)

    class Meta:
        db_table = 'cofk_union_publication'
