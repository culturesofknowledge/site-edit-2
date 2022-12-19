# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from core.helper import model_utils
from core.helper.model_utils import RecordTracker


class Recref(models.Model, RecordTracker):
    recref_id = models.AutoField(primary_key=True)
    from_date = models.DateField(null=True)
    to_date = models.DateField(null=True)

    relationship_type = models.CharField(max_length=100)

    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)

    class Meta:
        abstract = True


class CofkLookupDocumentType(models.Model):
    document_type_id = models.AutoField(primary_key=True)
    document_type_code = models.CharField(unique=True, max_length=3)
    document_type_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_lookup_document_type'


class CofkUnionComment(models.Model, RecordTracker):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_comment'


class CofkUnionNationality(models.Model):
    nationality_id = models.AutoField(primary_key=True)
    nationality_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_nationality'


class CofkUnionRelationship(models.Model, RecordTracker):
    relationship_id = models.AutoField(primary_key=True)
    left_table_name = models.CharField(max_length=100)
    left_id_value = models.CharField(max_length=100)
    relationship_type = models.ForeignKey('CofkUnionRelationshipType', models.DO_NOTHING, db_column='relationship_type')
    right_table_name = models.CharField(max_length=100)
    right_id_value = models.CharField(max_length=100)
    relationship_valid_from = models.DateTimeField(blank=True, null=True)
    relationship_valid_till = models.DateTimeField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)

    class Meta:
        db_table = 'cofk_union_relationship'


class CofkUnionRelationshipType(models.Model, RecordTracker):
    relationship_code = models.CharField(primary_key=True, max_length=50)
    desc_left_to_right = models.CharField(max_length=200)
    desc_right_to_left = models.CharField(max_length=200)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)

    class Meta:
        db_table = 'cofk_union_relationship_type'


class CofkUnionResource(models.Model, RecordTracker):
    resource_id = models.AutoField(primary_key=True)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_resource'


class CofkUnionSpeedEntryText(models.Model):
    speed_entry_text_id = models.AutoField(primary_key=True)
    object_type = models.CharField(max_length=30)
    speed_entry_text = models.CharField(max_length=200)

    class Meta:
        db_table = 'cofk_union_speed_entry_text'


class CopyCofkUnionQueryableWork(models.Model):
    iwork_id = models.IntegerField(blank=True, null=True)
    work_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_of_work_std = models.DateField(blank=True, null=True)
    date_of_work_std_year = models.IntegerField(blank=True, null=True)
    date_of_work_std_month = models.IntegerField(blank=True, null=True)
    date_of_work_std_day = models.IntegerField(blank=True, null=True)
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    date_of_work_inferred = models.SmallIntegerField(blank=True, null=True)
    date_of_work_uncertain = models.SmallIntegerField(blank=True, null=True)
    date_of_work_approx = models.SmallIntegerField(blank=True, null=True)
    creators_searchable = models.TextField(blank=True, null=True)
    creators_for_display = models.TextField(blank=True, null=True)
    authors_as_marked = models.TextField(blank=True, null=True)
    notes_on_authors = models.TextField(blank=True, null=True)
    authors_inferred = models.SmallIntegerField(blank=True, null=True)
    authors_uncertain = models.SmallIntegerField(blank=True, null=True)
    addressees_searchable = models.TextField(blank=True, null=True)
    addressees_for_display = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    addressees_inferred = models.SmallIntegerField(blank=True, null=True)
    addressees_uncertain = models.SmallIntegerField(blank=True, null=True)
    places_from_searchable = models.TextField(blank=True, null=True)
    places_from_for_display = models.TextField(blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    origin_inferred = models.SmallIntegerField(blank=True, null=True)
    origin_uncertain = models.SmallIntegerField(blank=True, null=True)
    places_to_searchable = models.TextField(blank=True, null=True)
    places_to_for_display = models.TextField(blank=True, null=True)
    destination_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.SmallIntegerField(blank=True, null=True)
    destination_uncertain = models.SmallIntegerField(blank=True, null=True)
    manifestations_searchable = models.TextField(blank=True, null=True)
    manifestations_for_display = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    people_mentioned = models.TextField(blank=True, null=True)
    images = models.TextField(blank=True, null=True)
    related_resources = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    work_is_translation = models.SmallIntegerField(blank=True, null=True)
    flags = models.TextField(blank=True, null=True)
    edit_status = models.CharField(max_length=3, blank=True, null=True)
    general_notes = models.TextField(blank=True, null=True)
    original_catalogue = models.CharField(max_length=100, blank=True, null=True)
    accession_code = models.CharField(max_length=1000, blank=True, null=True)
    work_to_be_deleted = models.SmallIntegerField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50, blank=True, null=True)
    drawer = models.CharField(max_length=50, blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    manifestation_type = models.CharField(max_length=50, blank=True, null=True)
    original_notes = models.TextField(blank=True, null=True)
    relevant_to_cofk = models.CharField(max_length=1, blank=True, null=True)
    subjects = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'copy_cofk_union_queryable_work'
