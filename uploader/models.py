import uuid

from django.db import models


class CofkCollectStatus(models.Model):
    class Meta:
        db_table = 'cofk_collect_status'

    status_id = models.AutoField(primary_key=True)
    status_desc = models.CharField(max_length=100, null=False)
    editable = models.IntegerField(null=False, default=1)


class CofkCollectToolUser(models.Model):
    class Meta:
        db_table = 'cofk_collect_tool_user'

    tool_user_id = models.AutoField(primary_key=True)
    tool_user_email = models.CharField(max_length=100, null=False, unique=True)
    tool_user_surname = models.CharField(max_length=100, null=False)
    tool_user_forename = models.CharField(max_length=100, null=False)
    tool_user_pw = models.CharField(max_length=100, null=False)


class CofkLookupCatalogue(models.Model):
    class Meta:
        db_table = 'cofk_lookup_catalogue'

    catalogue_id = models.AutoField(primary_key=True)
    catalogue_code = models.CharField(max_length=100, null=False, unique=True, default='')
    catalogue_name = models.CharField(max_length=500, null=False, unique=True, default='')
    is_in_union = models.IntegerField(null=False, default=1)
    publish_status = models.IntegerField(null=False, default=0)


class CofkReportGroup(models.Model):
    class Meta:
        db_table = 'cofk_report_groups'

    report_group_id = models.AutoField(primary_key=True)
    report_group_title = models.TextField()
    report_group_order = models.IntegerField(null=False, default=1)
    on_main_reports_menu = models.IntegerField(null=False, default=0)
    report_group_code = models.CharField(max_length=100)


class CofkUnionAuditLiteral(models.Model):
    class Meta:
        db_table = 'cofk_union_audit_literal'

    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    change_user = models.CharField(max_length=50)
    change_type = models.CharField(max_length=3, null=False)
    table_name = models.CharField(max_length=100, null=False)
    key_value_text = models.CharField(max_length=100, null=False)
    key_value_integer = models.IntegerField()
    key_decode = models.TextField()
    column_name = models.CharField(max_length=100, null=False)
    new_column_value = models.TextField()
    old_column_value = models.TextField()


class CofkUnionAuditRelationship(models.Model):
    class Meta:
        db_table = 'cofk_union_audit_relationship'

    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    change_user = models.CharField(max_length=50)
    change_type = models.CharField(max_length=3, null=False)
    left_table_name = models.CharField(max_length=100, null=False)
    left_id_value_new = models.CharField(max_length=100, null=False, default='')
    left_id_decode_new = models.TextField(null=False, default='')
    left_id_value_old = models.CharField(max_length=100, null=False, default='')
    left_id_decode_old = models.TextField(null=False, default='')
    relationship_type = models.CharField(max_length=100, null=False)
    relationship_decode_left_to_right = models.CharField(max_length=100, null=False, default='')
    relationship_decode_right_to_left = models.CharField(max_length=100, null=False, default='')
    right_table_name = models.CharField(max_length=100, null=False)
    right_id_value_new = models.CharField(max_length=100, null=False, default='')
    right_id_decode_new = models.TextField(null=False, default='')
    right_id_value_old = models.CharField(max_length=100, null=False, default='')
    right_id_decode_old = models.TextField(null=False, default='')


class CofkUnionImage(models.Model):
    class Meta:
        db_table = 'cofk_union_image'

    image_id = models.AutoField(primary_key=True)
    image_filename = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(auto_now=True)
    change_user = models.CharField(max_length=50)
    thumbnail = models.TextField()
    can_be_displayed = models.CharField(max_length=1, null=False, default='Y')
    display_order = models.IntegerField(null=False, default=1)
    licence_details = models.TextField(null=False, default='')
    licence_url = models.CharField(max_length=2000, null=False, default='')
    credits = models.CharField(max_length=2000, null=False, default='')
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkUnionOrgType(models.Model):
    class Meta:
        db_table = 'cofk_union_org_type'

    org_type_id = models.AutoField(primary_key=True)
    org_type_desc = models.CharField(max_length=100, null=False, default='')


class CofkUnionPublication(models.Model):
    class Meta:
        db_table = 'cofk_union_publication'

    publication_id = models.AutoField(primary_key=True)
    publication_details = models.TextField(null=False, default='')
    change_timestamp = models.DateTimeField(auto_now=True)
    change_user = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=50, null=False, default='')


class CofkUnionRoleCategory(models.Model):
    class Meta:
        db_table = 'cofk_union_role_category'

    role_category_id = models.AutoField(primary_key=True)
    role_category_desc = models.CharField(max_length=100, null=False, default='')


class CofkUnionSubject(models.Model):
    class Meta:
        db_table = 'cofk_union_subject'

    subject_id = models.AutoField(primary_key=True)
    subject_desc = models.CharField(max_length=100, null=False, default='')


class Iso639LanguageCode(models.Model):
    class Meta:
        db_table = 'iso_639_language_codes'

    code_639_3 = models.CharField(max_length=3, default='')
    code_639_1 = models.CharField(max_length=2, null=True, default='')
    language_name = models.CharField(max_length=100, null=False, default='')
    language_id = models.AutoField(primary_key=True)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.upload_username, filename)


class CofkCollectUpload(models.Model):
    upload_id = models.AutoField(primary_key=True)
    upload_username = models.CharField(max_length=100, null=False)
    upload_description = models.TextField()
    upload_status = models.ForeignKey("uploader.CofkCollectStatus", null=False, default="1",
                                      on_delete=models.DO_NOTHING)
    upload_timestamp = models.DateTimeField(auto_now=True)
    total_works = models.IntegerField(null=False, default=0)
    works_accepted = models.IntegerField(null=False, default=0)
    works_rejected = models.IntegerField(null=False, default=0)
    uploader_email = models.CharField(max_length=250, null=False, default='')
    _id = models.CharField(max_length=32)
    upload_name = models.CharField(max_length=254)
    upload_file = models.FileField(upload_to=user_directory_path)


class CofkReport(models.Model):
    class Meta:
        db_table = 'cofk_reports'

    report_id = models.AutoField(primary_key=True)
    report_title = models.TextField()
    class_name = models.CharField(max_length=40)
    method_name = models.CharField(max_length=40)
    report_group_id = models.ForeignKey("uploader.CofkReportGroup", on_delete=models.DO_NOTHING)
    menu_item = models.ForeignKey('core.CofkMenu', models.DO_NOTHING, blank=True, null=True)
    has_csv_option = models.BooleanField(null=False, default=False)
    is_dummy_option = models.BooleanField(null=False, default=False)
    report_code = models.CharField(max_length=100)
    parm_list = models.TextField()
    parm_titles = models.TextField()
    prompt_for_parms = models.SmallIntegerField(null=False, default=0)
    default_parm_values = models.TextField()
    parm_methods = models.TextField()
    report_help = models.TextField()


class CofkUserSavedQuery(models.Model):
    class Meta:
        db_table = 'cofk_user_saved_queries'

    query_id = models.AutoField(primary_key=True)
    username = models.ForeignKey('login.CofkUsers', models.DO_NOTHING, db_column='username')
    query_class = models.CharField(max_length=100, null=False)
    query_method = models.CharField(max_length=100, null=False)
    query_title = models.TextField(null=False, default='')
    query_order_by = models.CharField(max_length=100, null=False, default='')
    query_sort_descending = models.SmallIntegerField(null=False, default=0)
    query_entries_per_page = models.SmallIntegerField(null=False, default=20)
    query_record_layout = models.CharField(max_length=12, null=False, default='across_page')
    query_menu_item_name = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
