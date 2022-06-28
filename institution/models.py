import uuid as uuid
from django.db import models


class CofkCollectInstitution(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    institution_id = models.AutoField(primary_key=True)
    # TODO under what circumstances is this populated? it is clearly not populated when spreadsheet is uploaded
    union_institution_id = models.OneToOneField("CofkUnionInstitution",
                                                null=True,
                                                on_delete=models.DO_NOTHING)
    institution_name = models.TextField(null=False, default='')
    institution_city = models.TextField(null=False, default='')
    institution_country = models.TextField(null=False, default='')
    upload_name = models.CharField(max_length=254)
    _id = models.CharField(max_length=32)
    institution_synonyms = models.TextField()
    institution_city_synonyms = models.TextField()
    institution_country_synonyms = models.TextField()


class CofkUnionInstitution(models.Model):
    institution_id = models.AutoField(primary_key=True)
    institution_name = models.TextField(null=False, default='')
    institution_synonyms = models.TextField(null=False, default='')
    institution_city = models.TextField(null=False, default='')
    institution_city_synonyms = models.TextField(null=False, default='')
    institution_country = models.TextField(null=False, default='')
    institution_country_synonyms = models.TextField(null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    editors_notes = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4)
    address = models.TextField()
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)


class CofkCollectInstitutionResource(models.Model):
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    resource_id = models.AutoField(primary_key=True)
    institution_id = models.IntegerField(null=False)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')
