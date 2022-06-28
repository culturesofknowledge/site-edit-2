import uuid as uuid
from django.db import models

# Create your models here.


class CofkCollectInstitution(models.Model):
    #class Meta:
    #    db_table = 'cofk_collect_institution'

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    # upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    institution_id = models.AutoField(primary_key=True)
    # union_institution_id = Column(ForeignKey('cofk_union_institution.institution_id', ondelete='SET NULL'))
    # union_institution_id = models.ForeignKey("uploader.CofkUnionInstitution", on_delete=models.SET_NULL)
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

    # union_institution = relationship('CofkUnionInstitution')
    # upload = relationship('CofkCollectUpload')


class CofkUnionInstitution(models.Model):
    #class Meta:
    #    db_table = 'cofk_union_institution'

    institution_id = models.AutoField(primary_key=True)
    institution_name = models.TextField(null=False, default='')
    institution_synonyms = models.TextField(null=False, default='')
    institution_city = models.TextField(null=False, default='')
    institution_city_synonyms = models.TextField(null=False, default='')
    institution_country = models.TextField(null=False, default='')
    institution_country_synonyms = models.TextField(null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    editors_notes = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4)
    address = models.TextField()
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)


class CofkCollectInstitutionResource(models.Model):
    #class Meta:
    #    db_table = 'cofk_collect_institution_resource'

    # __table_args__ = (
    #    ForeignKeyConstraint(['upload_id', 'institution_id'], ['cofk_collect_institution.upload_id', 'cofk_collect_institution.institution_id']),
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    resource_id = models.AutoField(primary_key=True)
    institution_id = models.IntegerField(null=False)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')

    # upload = relationship('CofkCollectInstitution')
    # upload1 = relationship('CofkCollectUpload')