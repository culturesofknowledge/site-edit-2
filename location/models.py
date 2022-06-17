import uuid
from django.db import models

# Create your models here.

# KTODO Researchers' notes for front-end display
# KTODO Related resources

class CofkCollectLocation(models.Model):
    class Meta:
        db_table = 'cofk_collect_location'

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    location_id = models.AutoField(primary_key=True)
    # union_location_id = Column(ForeignKey('cofk_union_location.location_id', ondelete='SET NULL'))
    union_location_id = models.ForeignKey("location.CofkUnionLocation", on_delete=models.DO_NOTHING)
    location_name = models.CharField(max_length=500, null=False, default='')
    element_1_eg_room = models.CharField(max_length=100, null=False, default='')
    element_2_eg_building = models.CharField(max_length=100, null=False, default='')
    element_3_eg_parish = models.CharField(max_length=100, null=False, default='')
    element_4_eg_city = models.CharField(max_length=100, null=False, default='')
    element_5_eg_county = models.CharField(max_length=100, null=False, default='')
    element_6_eg_country = models.CharField(max_length=100, null=False, default='')
    element_7_eg_empire = models.CharField(max_length=100, null=False, default='')
    notes_on_place = models.TextField()
    editors_notes = models.TextField()
    upload_name = models.CharField(max_length=254)
    _id = models.CharField(max_length=32)
    location_synonyms = models.TextField()
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

    # union_location = relationship('CofkUnionLocation')
    # upload = relationship('CofkCollectUpload') # KTODO how to bind upload record

class CofkUnionLocation(models.Model):
    # KTODO who use this models ???
    class Meta:
        db_table = 'cofk_union_location'

    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=500, null=False, default='')
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    location_synonyms = models.TextField()
    editors_notes = models.TextField()
    element_1_eg_room = models.CharField(max_length=100, null=False, default='')
    element_2_eg_building = models.CharField(max_length=100, null=False, default='')
    element_3_eg_parish = models.CharField(max_length=100, null=False, default='')
    element_4_eg_city = models.CharField(max_length=100, null=False, default='')
    element_5_eg_county = models.CharField(max_length=100, null=False, default='')
    element_6_eg_country = models.CharField(max_length=100, null=False, default='')
    element_7_eg_empire = models.CharField(max_length=100, null=False, default='')
    uuid = models.UUIDField(default=uuid.uuid4)



class CofkCollectLocationResource(models.Model):
    class Meta:
        db_table = 'cofk_collect_location_resource'

    # __table_args__ = (
    #    ForeignKeyConstraint(['upload_id', 'location_id'], ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id']),
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    resource_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')

    # upload = relationship('CofkCollectLocation')
    # upload1 = relationship('CofkCollectUpload')

