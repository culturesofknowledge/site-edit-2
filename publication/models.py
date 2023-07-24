from django.db import models

from core.helper import model_serv
from core.helper.model_serv import RecordTracker


class CofkUnionPublication(models.Model, RecordTracker):
    publication_id = models.AutoField(primary_key=True)
    publication_details = models.TextField()
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=50)

    class Meta:
        db_table = 'cofk_union_publication'
