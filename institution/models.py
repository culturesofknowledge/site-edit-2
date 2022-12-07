from django.db import models

from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref


class CofkCollectInstitution(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", on_delete=models.CASCADE)
    institution_id = models.IntegerField()
    union_institution = models.ForeignKey('CofkUnionInstitution', models.DO_NOTHING, blank=True, null=True)
    institution_name = models.TextField(default='')
    institution_city = models.TextField(default='')
    institution_country = models.TextField(default='')
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)
    institution_synonyms = models.TextField(blank=True, null=True)
    institution_city_synonyms = models.TextField(blank=True, null=True)
    institution_country_synonyms = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_institution'
        unique_together = (('upload', 'institution_id'),)

    def __str__(self):
        return str(self.union_institution) if\
            self.union_institution is not None else f'{self.institution_name} (collect)'


class CofkUnionInstitution(models.Model, RecordTracker):
    institution_id = models.AutoField(primary_key=True)
    institution_name = models.TextField()
    institution_synonyms = models.TextField(blank=True, null=True)
    institution_city = models.TextField()
    institution_city_synonyms = models.TextField(blank=True, null=True)
    institution_country = models.TextField()
    institution_country_synonyms = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    editors_notes = models.TextField(blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)
    address = models.CharField(max_length=1000, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    @property
    def resources(self):
        return self.cofkinstitutionresourcemap_set.all()

    @property
    def images(self):
        return self.cofkinstitutionimagemap_set.all()

    class Meta:
        db_table = 'cofk_union_institution'


class CofkCollectInstitutionResource(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    institution_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_institution_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkInstitutionResourceMap(Recref):
    institution = models.ForeignKey(CofkUnionInstitution, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_institution_resource_map'


class CofkInstitutionImageMap(Recref):
    institution = models.ForeignKey(CofkUnionInstitution, on_delete=models.CASCADE)
    image = models.ForeignKey('uploader.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_institution_image_map'
