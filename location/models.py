from django.db import models

from core.helper import model_utils
# KTODO Researchers' notes for front-end display
# KTODO Related resources
from core.helper.model_utils import RecordTracker
from core.models import Recref


class CofkCollectLocation(models.Model):
    # KTODO why upload_id in database become upload_id_id, should I change field name to upload instead
    # KTODO change null=True for draft version
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE, null=True)
    location_id = models.AutoField(primary_key=True)
    # KTODO what is usage of UnionLocation
    union_location = models.ForeignKey('CofkUnionLocation', models.DO_NOTHING, blank=True, null=True)

    location_name = models.CharField(max_length=500)
    element_1_eg_room = models.CharField(max_length=100)
    element_2_eg_building = models.CharField(max_length=100)
    element_3_eg_parish = models.CharField(max_length=100)
    element_4_eg_city = models.CharField(max_length=100)
    element_5_eg_county = models.CharField(max_length=100)
    element_6_eg_country = models.CharField(max_length=100)
    element_7_eg_empire = models.CharField(max_length=100)
    notes_on_place = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)  # KTODO what is this _id, should be remove??
    location_synonyms = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_location'
        unique_together = (('upload', 'location_id'),)

    def __str__(self):
        return str(self.union_location) if self.union_location is not None else f'{self.location_name} (collect)'


class CofkUnionLocation(models.Model, RecordTracker):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=500)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
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

    images = models.ManyToManyField('uploader.CofkUnionImage')  # TOBEREMOVE

    @property
    def comments(self):
        return self.cofklocationcommentmap_set.all()

    @property
    def resources(self):
        return self.cofklocationresourcemap_set.all()

    def __str__(self):
        return self.location_name

    class Meta:
        db_table = 'cofk_union_location'


class CofkCollectLocationResource(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    location_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_location_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkLocationCommentMap(Recref):
    location = models.ForeignKey(CofkUnionLocation, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_location_comment_map'


class CofkLocationResourceMap(Recref):
    location = models.ForeignKey(CofkUnionLocation, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_location_resource_map'


class CofkLocationImageMap(Recref):
    location = models.ForeignKey(CofkUnionLocation, on_delete=models.CASCADE)
    image = models.ForeignKey('uploader.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_location_image_map'
