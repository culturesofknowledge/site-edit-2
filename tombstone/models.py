from django.db import models

from core.helper import model_serv
from core.helper.model_serv import RecordTracker


class TombstoneRequest(models.Model, RecordTracker):
    tombstone_req_id = models.AutoField(primary_key=True)
    sql = models.TextField(blank=True, null=True)
    sql_params = models.BinaryField(blank=True, null=True)
    result_jsonl = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=0)
    model_name = models.CharField(max_length=100)

    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
