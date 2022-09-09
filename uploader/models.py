from django.db import models

from core.helper import model_utils
from core.helper.model_utils import RecordTracker


class CofkCollectStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_desc = models.CharField(max_length=100)
    editable = models.IntegerField(null=False, default=1)  # TODO schema changed for current system

    class Meta:
        db_table = 'cofk_collect_status'


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


class CofkReportGroup(models.Model):
    report_group_id = models.AutoField(primary_key=True)
    report_group_title = models.TextField(blank=True, null=True)
    report_group_order = models.IntegerField()
    on_main_reports_menu = models.IntegerField()
    report_group_code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cofk_report_group'


class CofkUnionAuditLiteral(models.Model):
    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    change_type = models.CharField(max_length=3)
    table_name = models.CharField(max_length=100)
    key_value_text = models.CharField(max_length=100)
    key_value_integer = models.IntegerField(blank=True, null=True)
    key_decode = models.TextField(blank=True, null=True)
    column_name = models.CharField(max_length=100)
    new_column_value = models.TextField(blank=True, null=True)
    old_column_value = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_audit_literal'


class CofkUnionAuditRelationship(models.Model):
    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    change_type = models.CharField(max_length=3)
    left_table_name = models.CharField(max_length=100)
    left_id_value_new = models.CharField(max_length=100)
    left_id_decode_new = models.TextField()
    left_id_value_old = models.CharField(max_length=100)
    left_id_decode_old = models.TextField()
    relationship_type = models.CharField(max_length=100)
    relationship_decode_left_to_right = models.CharField(max_length=100)
    relationship_decode_right_to_left = models.CharField(max_length=100)
    right_table_name = models.CharField(max_length=100)
    right_id_value_new = models.CharField(max_length=100)
    right_id_decode_new = models.TextField()
    right_id_value_old = models.CharField(max_length=100)
    right_id_decode_old = models.TextField()

    class Meta:
        db_table = 'cofk_union_audit_relationship'


class CofkUnionImage(models.Model, RecordTracker):
    image_id = models.AutoField(primary_key=True)
    image_filename = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    thumbnail = models.TextField(blank=True, null=True)
    can_be_displayed = models.CharField(max_length=1)
    display_order = models.IntegerField()
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
    code_639_3 = models.CharField(max_length=3)
    code_639_1 = models.CharField(max_length=2)
    language_name = models.CharField(max_length=100)
    language_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'iso639_language_code'


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


class CofkReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_title = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=40, blank=True, null=True)
    method_name = models.CharField(max_length=40, blank=True, null=True)
    report_group = models.ForeignKey(CofkReportGroup, models.DO_NOTHING, blank=True, null=True)
    menu_item = models.ForeignKey('core.CofkMenu', models.DO_NOTHING, blank=True, null=True)
    has_csv_option = models.BooleanField(null=False, default=False)
    is_dummy_option = models.BooleanField(null=False, default=False)
    report_code = models.CharField(max_length=100, blank=True, null=True)
    parm_list = models.TextField(blank=True, null=True)
    parm_titles = models.TextField(blank=True, null=True)
    prompt_for_parms = models.SmallIntegerField()
    default_parm_values = models.TextField(blank=True, null=True)
    parm_methods = models.TextField(blank=True, null=True)
    report_help = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_report'


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


class CofkUnionFavouriteLanguage(models.Model):
    language_code = models.OneToOneField(Iso639LanguageCode, models.DO_NOTHING, db_column='language_code',
                                         primary_key=True)

    class Meta:
        db_table = 'cofk_union_favourite_language'
