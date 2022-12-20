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


class CofkUnionImage(models.Model, RecordTracker):
    image_id = models.AutoField(primary_key=True)
    image_filename = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    thumbnail = models.TextField(blank=True, null=True)
    can_be_displayed = models.CharField(max_length=1)
    display_order = models.IntegerField(default=1)
    licence_details = models.TextField()
    licence_url = models.CharField(max_length=2000)
    credits = models.CharField(max_length=2000)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_image'


class CofkUnionOrgType(models.Model):
    org_type_id = models.AutoField(primary_key=True)
    org_type_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_org_type'


class CofkUnionRoleCategory(models.Model):
    role_category_id = models.AutoField(primary_key=True)
    role_category_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_role_category'


class CofkUnionSubject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_desc = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_union_subject'


class Iso639LanguageCode(models.Model):
    code_639_3 = models.CharField(max_length=3, unique=True)  # KTODO this is primary_key in original schema
    code_639_1 = models.CharField(max_length=2)
    language_name = models.CharField(max_length=100)
    language_id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.language_name

    class Meta:
        db_table = 'iso_639_language_codes'


class CofkUnionFavouriteLanguage(models.Model):
    language_code = models.OneToOneField(Iso639LanguageCode, models.DO_NOTHING, db_column='language_code',
                                         primary_key=True)

    class Meta:
        db_table = 'cofk_union_favourite_language'


class CofkLookupCatalogue(models.Model):
    catalogue_id = models.AutoField(primary_key=True)
    catalogue_code = models.CharField(unique=True, max_length=100)
    catalogue_name = models.CharField(unique=True, max_length=500)
    is_in_union = models.IntegerField()
    publish_status = models.SmallIntegerField()

    class Meta:
        db_table = 'cofk_lookup_catalogue'


class CofkUserSavedQuery(models.Model):
    query_id = models.AutoField(primary_key=True)
    username = models.ForeignKey('login.CofkUser', models.DO_NOTHING, db_column='username')
    query_class = models.CharField(max_length=100)
    query_method = models.CharField(max_length=100)
    query_title = models.TextField()
    query_order_by = models.CharField(max_length=100)
    query_sort_descending = models.SmallIntegerField()
    query_entries_per_page = models.SmallIntegerField()
    query_record_layout = models.CharField(max_length=12)
    query_menu_item_name = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)

    class Meta:
        db_table = 'cofk_user_saved_query'


class CofkUserSavedQuerySelection(models.Model):
    selection_id = models.AutoField(primary_key=True)
    query = models.ForeignKey(CofkUserSavedQuery, models.DO_NOTHING)
    column_name = models.CharField(max_length=100)
    column_value = models.CharField(max_length=500)
    op_name = models.CharField(max_length=100)
    op_value = models.CharField(max_length=100)
    column_value2 = models.CharField(max_length=500)

    class Meta:
        db_table = 'cofk_user_saved_query_selection'
