from django.db import models


# KTODO Researchers' notes for front-end display
# KTODO Related resources


class CofkCollectLocation(models.Model):
    # KTODO why upload_id in database become upload_id_id, should I change field name to upload instead
    # KTODO change null=True for draft version
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING, null=True)
    location_id = models.IntegerField()
    union_location = models.ForeignKey('CofkUnionLocation', models.DO_NOTHING, blank=True, null=True)

    # KTODO what is usage of UnionLocation
    # union_location_id = models.ForeignKey("location.CofkUnionLocation", on_delete=models.DO_NOTHING)
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


class CofkUnionLocation(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=500)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True)
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


class CofkCollectLocationResource(models.Model):
    # KTODO not sure when to use / assign value of `upload` field
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    location_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_location_resource'
        unique_together = (('upload', 'resource_id'),)
