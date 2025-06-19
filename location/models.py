from django.db import models

from core.helper import model_serv
from core.helper.model_serv import RecordTracker
from core.models import Recref


class CofkUnionLocation(models.Model, RecordTracker):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=500)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    is_tombstone = models.BooleanField(default=False, help_text="Mark as tombstone instead of deleting")
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    location_synonyms = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    element_1_eg_room = models.CharField(max_length=100)
    element_2_eg_building = models.CharField(max_length=100)
    element_3_eg_parish = models.CharField(max_length=100)
    element_4_eg_city = models.CharField(max_length=100)
    element_5_eg_county = models.CharField(max_length=100)
    element_6_eg_country = models.CharField(max_length=100)
    element_7_eg_empire = models.CharField(max_length=100)
    uuid = models.UUIDField(blank=True, null=True)
    comments = models.ManyToManyField('core.CofkUnionComment', through='CofkLocationCommentMap')
    resources = models.ManyToManyField('core.CofkUnionResource', through='CofkLocationResourceMap')
    images = models.ManyToManyField('core.CofkUnionImage', through='CofkLocationImageMap')
    works = models.ManyToManyField('work.CofkUnionWork', through='work.CofkWorkLocationMap')

    def __str__(self):
        return self.location_name

    class Meta:
        db_table = 'cofk_union_location'
        permissions = [
            ('export_file', 'Export csv/excel from search results'),
        ]


class CofkLocationCommentMap(Recref):
    location = models.ForeignKey(CofkUnionLocation, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_location_comment_map'
        indexes = [
            models.Index(fields=['location', 'relationship_type']),
        ]


class CofkLocationResourceMap(Recref):
    location = models.ForeignKey(CofkUnionLocation, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_location_resource_map'
        indexes = [
            models.Index(fields=['location', 'relationship_type']),
        ]


class CofkLocationImageMap(Recref):
    location = models.ForeignKey(CofkUnionLocation, on_delete=models.CASCADE)
    image = models.ForeignKey('core.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_location_image_map'
        indexes = [
            models.Index(fields=['location', 'relationship_type']),
        ]


