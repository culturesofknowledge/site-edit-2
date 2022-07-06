import uuid as uuid
from django.db import models


class CofkCollectPerson(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    iperson_id = models.AutoField(primary_key=True)
    person_id = models.OneToOneField("CofkUnionPerson", on_delete=models.DO_NOTHING, null=True)
    primary_name = models.CharField(max_length=200, null=False)
    alternative_names = models.TextField()
    roles_or_titles = models.TextField()
    gender = models.CharField(max_length=1, null=False, default='')
    is_organisation = models.CharField(max_length=1, null=False, default='')
    organisation_type = models.IntegerField(null=True)
    date_of_birth_year = models.IntegerField(null=True)
    date_of_birth_month = models.IntegerField(null=True)
    date_of_birth_day = models.IntegerField(null=True)
    date_of_birth_is_range = models.SmallIntegerField(null=True, default=0)
    date_of_birth2_year = models.IntegerField(null=True)
    date_of_birth2_month = models.IntegerField(null=True)
    date_of_birth2_day = models.IntegerField(null=True)
    date_of_birth_inferred = models.SmallIntegerField(null=True, default=0)
    date_of_birth_uncertain = models.SmallIntegerField(null=True, default=0)
    date_of_birth_approx = models.SmallIntegerField(null=True, default=0)
    date_of_death_year = models.IntegerField(null=True)
    date_of_death_month = models.IntegerField(null=True)
    date_of_death_day = models.IntegerField(null=True)
    date_of_death_is_range = models.SmallIntegerField(null=True, default=0)
    date_of_death2_year = models.IntegerField(null=True)
    date_of_death2_month = models.IntegerField(null=True)
    date_of_death2_day = models.IntegerField(null=True)
    date_of_death_inferred = models.SmallIntegerField(null=True, default=0)
    date_of_death_uncertain = models.SmallIntegerField(null=True, default=0)
    date_of_death_approx = models.SmallIntegerField(null=True, default=0)
    flourished_year = models.IntegerField(null=True)
    flourished_month = models.IntegerField(null=True)
    flourished_day = models.IntegerField(null=True)
    flourished_is_range = models.SmallIntegerField(null=True, default=0)
    flourished2_year = models.IntegerField(null=True)
    flourished2_month = models.IntegerField(null=True)
    flourished2_day = models.IntegerField(null=True)
    notes_on_person = models.TextField(null=True)
    editors_notes = models.TextField(null=True)
    upload_name = models.CharField(max_length=254)
    _id = models.CharField(max_length=32)


class CofkUnionPerson(models.Model):
    person_id = models.CharField(max_length=100, primary_key=True)
    foaf_name = models.CharField(max_length=200, null=False)
    skos_altlabel = models.TextField()
    skos_hiddenlabel = models.TextField()
    person_aliases = models.TextField()
    date_of_birth_year = models.IntegerField()
    date_of_birth_month = models.IntegerField()
    date_of_birth_day = models.IntegerField()
    date_of_birth = models.DateField()
    date_of_birth_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_birth_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_birth_approx = models.SmallIntegerField(null=False, default=0)
    date_of_death_year = models.IntegerField()
    date_of_death_month = models.IntegerField()
    date_of_death_day = models.IntegerField()
    date_of_death = models.DateField()
    date_of_death_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_death_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_death_approx = models.SmallIntegerField(null=False, default=0)
    gender = models.CharField(max_length=1, null=False, default='')
    is_organisation = models.CharField(max_length=1, null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    editors_notes = models.TextField()
    further_reading = models.TextField()
    organisation_type = models.ForeignKey("uploader.CofkUnionOrgType", on_delete=models.DO_NOTHING)
    date_of_birth_calendar = models.CharField(max_length=2, null=False, default='')
    date_of_birth_is_range = models.SmallIntegerField(null=False, default=0)
    date_of_birth2_year = models.IntegerField()
    date_of_birth2_month = models.IntegerField()
    date_of_birth2_day = models.IntegerField()
    date_of_death_calendar = models.CharField(max_length=2, null=False, default='')
    date_of_death_is_range = models.SmallIntegerField(null=False, default=0)
    date_of_death2_year = models.IntegerField()
    date_of_death2_month = models.IntegerField()
    date_of_death2_day = models.IntegerField()
    flourished = models.DateField()
    flourished_calendar = models.CharField(max_length=2, null=False, default='')
    flourished_is_range = models.SmallIntegerField(null=False, default=0)
    flourished_year = models.IntegerField()
    flourished_month = models.IntegerField()
    flourished_day = models.IntegerField()
    flourished2_year = models.IntegerField()
    flourished2_month = models.IntegerField()
    flourished2_day = models.IntegerField()
    uuid = models.UUIDField(default=uuid.uuid4)
    flourished_inferred = models.SmallIntegerField(null=False, default=0)
    flourished_uncertain = models.SmallIntegerField(null=False, default=0)
    flourished_approx = models.SmallIntegerField(null=False, default=0)


class CofkCollectOccupationOfPerson(models.Model):
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    occupation_of_person_id = models.AutoField(primary_key=True)
    iperson_id = models.IntegerField(null=False)
    occupation_id = models.ForeignKey("uploader.CofkUnionRoleCategory", on_delete=models.CASCADE, null=False)


class CofkCollectPersonResource(models.Model):
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    resource_id = models.AutoField(primary_key=True, null=False)
    iperson_id = models.IntegerField(null=False)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')
