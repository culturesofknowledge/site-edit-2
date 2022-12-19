from django.db import models

from core.helper import model_utils


class CofkCollectStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_desc = models.CharField(max_length=100)
    editable = models.IntegerField(null=False, default=1)  # TODO schema changed for current system

    class Meta:
        db_table = 'cofk_collect_status'

    def __str__(self):
        return self.status_desc


class CofkCollectToolUser(models.Model):
    tool_user_id = models.AutoField(primary_key=True)
    tool_user_email = models.CharField(unique=True, max_length=100)
    tool_user_surname = models.CharField(max_length=100)
    tool_user_forename = models.CharField(max_length=100)
    tool_user_pw = models.CharField(max_length=100)

    class Meta:
        db_table = 'cofk_collect_tool_user'


class CofkLookupCatalogue(models.Model):
    catalogue_id = models.AutoField(primary_key=True)
    catalogue_code = models.CharField(unique=True, max_length=100)
    catalogue_name = models.CharField(unique=True, max_length=500)
    is_in_union = models.IntegerField()
    publish_status = models.SmallIntegerField()

    class Meta:
        db_table = 'cofk_lookup_catalogue'


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.upload_username, filename)


class CofkCollectUpload(models.Model):
    upload_id = models.AutoField(primary_key=True)
    upload_username = models.CharField(max_length=100)
    upload_description = models.TextField(blank=True, null=True)
    upload_status = models.ForeignKey(CofkCollectStatus, models.DO_NOTHING, db_column='upload_status')
    upload_timestamp = models.DateTimeField()
    total_works = models.IntegerField()
    works_accepted = models.IntegerField()
    works_rejected = models.IntegerField()
    uploader_email = models.CharField(max_length=250)
    _id = models.CharField(max_length=32, blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    upload_file = models.FileField(upload_to=user_directory_path)  # TODO schema changed for current system

    class Meta:
        db_table = 'cofk_collect_upload'


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


class CofkCollectToolSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    session_timestamp = models.DateTimeField()
    session_code = models.TextField(unique=True, blank=True, null=True)
    username = models.ForeignKey(CofkCollectToolUser, models.DO_NOTHING, db_column='username', blank=True,
                                 null=True)

    class Meta:
        db_table = 'cofk_collect_tool_session'


