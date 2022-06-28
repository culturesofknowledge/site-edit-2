import uuid

from django.db import models

# Create your models here.

'''
def current_user():
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_user()")
        row = cursor.fetchone()

    return row
'''


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


'''
class CofkHelpPage(models.Model):
    class Meta:
        db_table = 'cofk_help_pages'

    page_id = models.AutoField(primary_key=True)
    page_title = models.CharField(max_length=500, null=False)
    custom_url = models.CharField(max_length=500)
    published_text = models.TextField(null=False, default='Sorry, no help currently available.')
    draft_text = models.TextField()
'''


class CofkLookupCatalogue(models.Model):
    class Meta:
        db_table = 'cofk_lookup_catalogue'

    catalogue_id = models.AutoField(primary_key=True)
    catalogue_code = models.CharField(max_length=100, null=False, unique=True, default='')
    catalogue_name = models.CharField(max_length=500, null=False, unique=True, default='')
    is_in_union = models.IntegerField(null=False, default=1)
    publish_status = models.IntegerField(null=False, default=0)


'''
class CofkLookupDocumentType(models.Model):
    class Meta:
        db_table = 'cofk_lookup_document_type'

    document_type_id = models.AutoField(primary_key=True)
    document_type_code = models.CharField(max_length=3, null=False, unique=True)
    document_type_desc = models.CharField(max_length=100, null=False)


class CofkMenu(models.Model):
    class Meta:
        db_table = 'cofk_menu'

    # __table_args__ = (
    #    CheckConstraint('((has_children = 0) AND (class_name IS NOT NULL) AND (method_name IS NOT NULL)) OR ((has_children = 1) AND (class_name IS NULL) AND (method_name IS NULL))'),
    #    CheckConstraint('(called_as_popup = 0) OR (called_as_popup = 1)')
    # )

    menu_item_id = models.AutoField(primary_key=True)
    menu_item_name = models.TextField(null=False)
    # menu_order = models.AutoField()
    # meno_order = models.ForeignKey('uploader.CofkMenu', on_delete=models.DO_NOTHING)
    # parent_id = Column(ForeignKey('cofk_menu.menu_item_id'))
    parent_id = models.ForeignKey("uploader.CofkMenu", on_delete=models.DO_NOTHING)
    has_children = models.IntegerField(null=False, default=0)
    class_name = models.CharField(max_length=100)
    method_name = models.CharField(max_length=100)
    user_restriction = models.CharField(max_length=30, null=False, default='')
    hidden_parent = models.IntegerField()
    called_as_popup = models.IntegerField(null=False, default=0)
    collection = models.CharField(max_length=20, null=False, default='')

    # parent = relationship('CofkMenu', remote_side=[menu_item_id])
'''


class CofkReportGroup(models.Model):
    class Meta:
        db_table = 'cofk_report_groups'

    report_group_id = models.AutoField(primary_key=True)
    report_group_title = models.TextField()
    report_group_order = models.IntegerField(null=False, default=1)
    on_main_reports_menu = models.IntegerField(null=False, default=0)
    report_group_code = models.CharField(max_length=100)


# Assuming this table contain report formats, can perhaps be stored
# elsewhere, not in a db table
# t_cofk_report_outputs = Table(
#    'cofk_report_outputs', metadata,
#    Column('output_id', String(250), null=False, default=''),
#    Column('line_number', Integer, null=False, default=0),
#    Column('line_text', Text)
# )


# TODO
# CofkRole is system user role, not role for subject persons
# This will probably be handled by Django's user groups
'''
class CofkRole(models.Model):
    class Meta:
        db_table = 'cofk_roles'

    role_id = models.AutoField(primary_key=True)
    role_code = models.CharField(max_length=20, null=False, unique=True, default='')
    role_name = models.TextField(null=False, unique=True, default='')

    # cofk_users = relationship('CofkUser', secondary='cofk_user_roles')
'''


class CofkUnionAuditLiteral(models.Model):
    class Meta:
        db_table = 'cofk_union_audit_literal'

    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    change_type = models.CharField(max_length=3, null=False)
    table_name = models.CharField(max_length=100, null=False)
    key_value_text = models.CharField(max_length=100, null=False)
    key_value_integer = models.IntegerField()
    key_decode = models.TextField()
    column_name = models.CharField(max_length=100, null=False)
    new_column_value = models.TextField()
    old_column_value = models.TextField()


# Optimization possible down the road? Is this a heavy handed way of
# creating table relationships?
class CofkUnionAuditRelationship(models.Model):
    class Meta:
        db_table = 'cofk_union_audit_relationship'

    audit_id = models.AutoField(primary_key=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
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


class CofkUnionComment(models.Model):
    class Meta:
        db_table = 'cofk_union_comment'

    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkUnionImage(models.Model):
    class Meta:
        db_table = 'cofk_union_image'

    image_id = models.AutoField(primary_key=True)
    image_filename = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    thumbnail = models.TextField()
    can_be_displayed = models.CharField(max_length=1, null=False, default='Y')
    display_order = models.IntegerField(null=False, default=1)
    licence_details = models.TextField(null=False, default='')
    licence_url = models.CharField(max_length=2000, null=False, default='')
    credits = models.CharField(max_length=2000, null=False, default='')
    uuid = models.UUIDField(default=uuid.uuid4)


'''
class CofkUnionNationality(models.Model):
    class Meta:
        db_table = 'cofk_union_nationality'

    nationality_id = models.AutoField(primary_key=True)
    nationality_desc = models.CharField(max_length=100, null=False, default='')
'''


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
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    abbrev = models.CharField(max_length=50, null=False, default='')


class CofkUnionRelationshipType(models.Model):
    class Meta:
        db_table = 'cofk_union_relationship_type'

    relationship_code = models.CharField(max_length=50, primary_key=True)
    desc_left_to_right = models.CharField(max_length=200, null=False, default='')
    desc_right_to_left = models.CharField(max_length=200, null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)


class CofkUnionResource(models.Model):
    class Meta:
        db_table = 'cofk_union_resource'

    resource_id = models.AutoField(primary_key=True)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkUnionRoleCategory(models.Model):
    class Meta:
        db_table = 'cofk_union_role_category'

    role_category_id = models.AutoField(primary_key=True)
    role_category_desc = models.CharField(max_length=100, null=False, default='')


'''
class CofkUnionSpeedEntryText(models.Model):
    class Meta:
        db_table = 'cofk_union_speed_entry_text'

    speed_entry_text_id = models.AutoField(primary_key=True)
    object_type = models.CharField(max_length=30, null=False, default='All')
    speed_entry_text = models.CharField(max_length=200, null=False, default='')
'''


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

    # TODO
    # Add favorite to config file or favorite field to above table?


'''
class CofkUnionFavouriteLanguage(Iso639LanguageCode):
    class Meta:
        db_table = 'cofk_union_favourite_language'

    # language_code = Column(ForeignKey('iso_639_language_codes.code_639_3', ondelete='CASCADE'), primary_key=True)
    # language_code = models.ForeignKey("uploader.Iso639LanguageCode.code_639_3", on_delete=models.CASCADE, primary_key=True)
    # language_code = models.OneToOneField("uploader.Iso639LanguageCode", on_delete=models.CASCADE)


class ProActivity(models.Model):
    class Meta:
        db_table = 'pro_activity'

    # __table_args__ = {'comment': 'prosopographical activity'}

    id = models.AutoField(primary_key=True)
    activity_type_id = models.TextField()
    activity_name = models.TextField()
    activity_description = models.TextField()
    date_type = models.TextField()
    date_from_year = models.TextField()
    date_from_month = models.TextField()
    date_from_day = models.TextField()
    date_from_uncertainty = models.TextField()
    date_to_year = models.TextField()
    date_to_month = models.TextField()
    date_to_day = models.TextField()
    date_to_uncertainty = models.TextField()
    notes_used = models.TextField()
    additional_notes = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.TextField()
    event_label = models.TextField()


class ProActivityRelation(models.Model):
    class Meta:
        db_table = 'pro_activity_relation'

    # __table_args__ = {'comment': 'mapping for related prosopography events'}

    id = models.AutoField(primary_key=True)
    meta_activity_id = models.IntegerField()
    filename = models.TextField(null=False)
    spreadsheet_row = models.IntegerField(null=False)
    combined_spreadsheet_row = models.IntegerField(null=False)


class ProAssertion(models.Model):
    class Meta:
        db_table = 'pro_assertion'

    id = models.AutoField(primary_key=True)
    assertion_type = models.TextField()
    assertion_id = models.TextField()
    source_id = models.TextField()
    source_description = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)


class ProLocation(models.Model):
    class Meta:
        db_table = 'pro_location'

    id = models.AutoField(primary_key=True)
    location_id = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)
    activity_id = models.IntegerField()


class ProPrimaryPerson(models.Model):
    class Meta:
        db_table = 'pro_primary_person'

    id = models.AutoField(primary_key=True)
    person_id = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)
    activity_id = models.IntegerField()


class ProRelationship(models.Model):
    class Meta:
        db_table = 'pro_relationship'

    id = models.AutoField(primary_key=True)
    subject_id = models.TextField()
    subject_type = models.TextField()
    subject_role_id = models.TextField()
    relationship_id = models.TextField()
    object_id = models.TextField()
    object_type = models.TextField()
    object_role_id = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)
    activity_id = models.IntegerField()


class ProRoleInActivity(models.Model):
    class Meta:
        db_table = 'pro_role_in_activity'

    id = models.AutoField(primary_key=True)
    entity_type = models.TextField()
    entity_id = models.TextField()
    role_id = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)
    activity_id = models.IntegerField()


class ProTextualSource(models.Model):
    class Meta:
        db_table = 'pro_textual_source'

    id = models.AutoField(primary_key=True)
    author = models.TextField()
    title = models.TextField()
    chapterArticleTitle = models.TextField()
    volumeSeriesNumber = models.TextField()
    issueNumber = models.TextField()
    pageNumber = models.TextField()
    editor = models.TextField()
    placePublication = models.TextField()
    datePublication = models.TextField()
    urlResource = models.TextField()
    abbreviation = models.TextField()
    fullBibliographicDetails = models.TextField()
    edition = models.TextField()
    reprintFacsimile = models.TextField()
    repository = models.TextField()
    # creation_user = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.TextField()
    change_timestamp = models.DateTimeField(auto_now=True)


class CofkCollectToolSession(models.Model):
    class Meta:
        db_table = 'cofk_collect_tool_session'

    session_id = models.AutoField(primary_key=True)
    session_timestamp = models.DateTimeField(auto_now=True)
    session_code = models.TextField(unique=True)
    # username = Column(ForeignKey('cofk_collect_tool_user.tool_user_email', ondelete='CASCADE', onupdate='CASCADE'))
    # Missing onupdate!!
    # username = models.ForeignKey("uploader.CofkCollectToolUser.tool_user_email", on_delete=models.CASCADE)
    username = models.OneToOneField("uploader.CofkCollectToolUser", on_delete=models.CASCADE)

    # cofk_collect_tool_user = relationship('CofkCollectToolUser')
'''


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.upload_username, filename)


class CofkCollectUpload(models.Model):
    #class Meta:
    #    db_table = 'cofk_collect_upload'

    upload_id = models.AutoField(primary_key=True)
    upload_username = models.CharField(max_length=100, null=False)
    upload_description = models.TextField()
    # upload_status = Column(ForeignKey('cofk_collect_status.status_id'), null=False, default=text("1"))
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

    # cofk_collect_statu = relationship('CofkCollectStatus')


'''
class CofkHelpOption(models.Model):
    class Meta:
        db_table = 'cofk_help_options'

    # __table_args__ = (
    #    UniqueConstraint('menu_item_id', 'button_name'),
    # )

    option_id = models.AutoField(primary_key=True)
    # menu_item_id = Column(ForeignKey('cofk_menu.menu_item_id'))
    menu_item_id = models.ForeignKey("uploader.CofkMenu", on_delete=models.DO_NOTHING)
    button_name = models.CharField(max_length=100, null=False, default='')
    # help_page_id = Column(ForeignKey('cofk_help_pages.page_id'), null=False)
    help_page_id = models.ForeignKey("uploader.CofkHelpPage", null=False, on_delete=models.DO_NOTHING)
    order_in_manual = models.IntegerField(null=False, default=0)
    menu_depth = models.IntegerField(null=False, default=0)

    # help_page = relationship('CofkHelpPage')
    # menu_item = relationship('CofkMenu')
'''


class CofkReport(models.Model):
    class Meta:
        db_table = 'cofk_reports'

    report_id = models.AutoField(primary_key=True)
    report_title = models.TextField()
    class_name = models.CharField(max_length=40)
    method_name = models.CharField(max_length=40)
    # report_group_id = Column(ForeignKey('cofk_report_groups.report_group_id'))
    report_group_id = models.ForeignKey("uploader.CofkReportGroup", on_delete=models.DO_NOTHING)
    # menu_item_id = Column(ForeignKey('cofk_menu.menu_item_id'))
    # menu_item_id = models.ForeignKey("uploader.CofkMenu", on_delete=models.DO_NOTHING)
    # has_csv_option = models.IntegerField(null=False, default=0)
    has_csv_option = models.BooleanField(null=False, default=False)
    # is_dummy_option = models.IntegerField(null=False, default=0)
    is_dummy_option = models.BooleanField(null=False, default=False)
    report_code = models.CharField(max_length=100)
    parm_list = models.TextField()
    parm_titles = models.TextField()
    prompt_for_parms = models.SmallIntegerField(null=False, default=0)
    default_parm_values = models.TextField()
    parm_methods = models.TextField()
    report_help = models.TextField()

    # menu_item = relationship('CofkMenu')
    # report_group = relationship('CofkReportGroup')


'''
class CofkSession(models.Model):
    class Meta:
        db_table = 'cofk_sessions'

    session_id = models.AutoField(primary_key=True)
    session_timestamp = models.DateTimeField(auto_now=True)
    session_code = models.TextField(unique=True)
    # username = Column(ForeignKey('cofk_users.username'))
    username = models.ForeignKey("uploader.CofkUser", on_delete=models.DO_NOTHING)

    # cofk_user = relationship('CofkUser')

class CofkUnionPersonSummary(CofkUnionPerson):
    class Meta:
        db_table = 'cofk_union_person_summary'

    # iperson_id = Column(ForeignKey('cofk_union_person.iperson_id', ondelete='CASCADE'), primary_key=True)
    other_details_summary = models.TextField()
    other_details_summary_searchable = models.TextField()
    sent = models.IntegerField(null=False, default=0)
    recd = models.IntegerField(null=False, default=0)
    all_works = models.IntegerField(null=False, default=0)
    mentioned = models.IntegerField(null=False, default=0)
    role_categories = models.TextField()
    images = models.TextField()
'''


# TODO
# The table below seems to map relationships manually between entities
# Can this be optimised?

class CofkUnionRelationship(models.Model):
    class Meta:
        db_table = 'cofk_union_relationship'

    # __table_args__ = (
    #    Index('cofk_union_relationship_right_idx', 'right_table_name', 'right_id_value', 'relationship_type'),
    #    Index('cofk_union_relationship_left_idx', 'left_table_name', 'left_id_value', 'relationship_type')
    # )

    relationship_id = models.AutoField(primary_key=True)
    left_table_name = models.CharField(max_length=100, null=False)
    left_id_value = models.CharField(max_length=100, null=False)
    # relationship_type = Column(ForeignKey('cofk_union_relationship_type.relationship_code'), null=False)
    relationship_type = models.ForeignKey("uploader.CofkUnionRelationshipType", null=False, on_delete=models.DO_NOTHING)
    right_table_name = models.CharField(max_length=100, null=False)
    right_id_value = models.CharField(max_length=100, null=False)
    relationship_valid_from = models.DateTimeField()
    relationship_valid_till = models.DateTimeField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)

    # cofk_union_relationship_type = relationship('CofkUnionRelationshipType')

# TODO
# The below table could be optimized. In addition, do favorite or popular queries
# have to be saved in the database?


class CofkUserSavedQuery(models.Model):
    class Meta:
        db_table = 'cofk_user_saved_queries'

    query_id = models.AutoField(primary_key=True)
    # username = Column(ForeignKey('cofk_users.username'), null=False, default=text("\"current_user\"()"))
    query_class = models.CharField(max_length=100, null=False)
    query_method = models.CharField(max_length=100, null=False)
    query_title = models.TextField(null=False, default='')
    query_order_by = models.CharField(max_length=100, null=False, default='')
    query_sort_descending = models.SmallIntegerField(null=False, default=0)
    query_entries_per_page = models.SmallIntegerField(null=False, default=20)
    query_record_layout = models.CharField(max_length=12, null=False, default='across_page')
    query_menu_item_name = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)

    # cofk_user = relationship('CofkUser')


'''
class CofkUnionQueryableWork(models.Model):
    class Meta:
        db_table = 'cofk_union_queryable_work'

    iwork_id = models.AutoField(primary_key=True)
    # work_id = Column(ForeignKey('cofk_union_work.work_id', ondelete='CASCADE'), null=False, unique=True)
    # work_id = models.ForeignKey("uploader.CofkUnionWork", on_delete=models.CASCADE, null=False, unique=True)
    work_id = models.OneToOneField("uploader.CofkUnionWork", on_delete=models.CASCADE, null=False)
    description = models.TextField()
    date_of_work_std = models.DateField()
    date_of_work_std_year = models.IntegerField()
    date_of_work_std_month = models.IntegerField()
    date_of_work_std_day = models.IntegerField()
    date_of_work_as_marked = models.CharField(max_length=250)
    # TODO
    # Boo
    date_of_work_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_work_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_work_approx = models.SmallIntegerField(null=False, default=0)
    creators_searchable = models.TextField(null=False, default='')
    creators_for_display = models.TextField(null=False, default='')
    authors_as_marked = models.TextField()
    notes_on_authors = models.TextField()
    authors_inferred = models.SmallIntegerField(null=False, default=0)
    authors_uncertain = models.SmallIntegerField(null=False, default=0)
    addressees_searchable = models.TextField(null=False, default='')
    addressees_for_display = models.TextField(null=False, default='')
    addressees_as_marked = models.TextField()
    addressees_inferred = models.SmallIntegerField(null=False, default=0)
    addressees_uncertain = models.SmallIntegerField(null=False, default=0)
    places_from_searchable = models.TextField(null=False, default='')
    places_from_for_display = models.TextField(null=False, default='')
    origin_as_marked = models.TextField()
    origin_inferred = models.SmallIntegerField(null=False, default=0)
    origin_uncertain = models.SmallIntegerField(null=False, default=0)
    places_to_searchable = models.TextField(null=False, default='')
    places_to_for_display = models.TextField(null=False, default='')
    destination_as_marked = models.TextField()
    destination_inferred = models.SmallIntegerField(null=False, default=0)
    destination_uncertain = models.SmallIntegerField(null=False, default=0)
    manifestations_searchable = models.TextField(null=False, default='')
    manifestations_for_display = models.TextField(null=False, default='')
    abstract = models.TextField()
    keywords = models.TextField()
    people_mentioned = models.TextField()
    images = models.TextField()
    related_resources = models.TextField()
    language_of_work = models.CharField(max_length=255)
    work_is_translation = models.SmallIntegerField(null=False, default=0)
    flags = models.TextField()
    edit_status = models.CharField(max_length=3, null=False, default='')
    general_notes = models.TextField()
    original_catalogue = models.CharField(max_length=100, null=False, default='')
    accession_code = models.CharField(max_length=1000)
    work_to_be_deleted = models.SmallIntegerField(null=False, default=0)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    drawer = models.CharField(max_length=50)
    editors_notes = models.TextField()
    manifestation_type = models.CharField(max_length=50)
    original_notes = models.TextField()
    relevant_to_cofk = models.CharField(max_length=1, null=False, default='')
    subjects = models.TextField()

    # work = relationship('CofkUnionWork', uselist=False)


class CofkUserSavedQuerySelection(models.Model):
    class Meta:
        db_table = 'cofk_user_saved_query_selection'

    selection_id = models.AutoField(primary_key=True)
    # query_id = Column(ForeignKey('cofk_user_saved_queries.query_id'), null=False)
    query_id = models.ForeignKey("uploader.CofkUserSavedQuery", null=False, on_delete=models.DO_NOTHING)
    column_name = models.CharField(max_length=100, null=False)
    column_value = models.CharField(max_length=500, null=False)
    op_name = models.CharField(max_length=100, null=False)
    op_value = models.CharField(max_length=100, null=False)
    column_value2 = models.CharField(max_length=500, null=False, default='')

    # query = relationship('CofkUserSavedQuery')
'''