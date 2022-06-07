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

    def is_empty(self):
        return self.objects.exists()


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


class CofkUnionInstitution(models.Model):
    class Meta:
        db_table = 'cofk_union_institution'

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


class CofkUnionLocation(models.Model):
    class Meta:
        db_table = 'cofk_union_location'

    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=500, null=False, default='')
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    location_synonyms = models.TextField()
    editors_notes = models.TextField()
    element_1_eg_room = models.CharField(max_length=100, null=False, default='')
    element_2_eg_building = models.CharField(max_length=100, null=False, default='')
    element_3_eg_parish = models.CharField(max_length=100, null=False, default='')
    element_4_eg_city = models.CharField(max_length=100, null=False, default='')
    element_5_eg_county = models.CharField(max_length=100, null=False, default='')
    element_6_eg_country = models.CharField(max_length=100, null=False, default='')
    element_7_eg_empire = models.CharField(max_length=100, null=False, default='')
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkUnionManifestation(models.Model):
    class Meta:
        db_table = 'cofk_union_manifestation'

    # __table_args__ = (
    #    CheckConstraint('(manifestation_creation_date_approx = 0) OR (manifestation_creation_date_approx = 1)'),
    #    CheckConstraint('(manifestation_creation_date_inferred = 0) OR (manifestation_creation_date_inferred = 1)'),
    #    CheckConstraint('(manifestation_creation_date_uncertain = 0) OR (manifestation_creation_date_uncertain = 1)')
    # )

    # TODO
    # Above fields should be boolean fields

    manifestation_id = models.CharField(max_length=100, primary_key=True)
    manifestation_type = models.CharField(max_length=3, null=False, default='')
    id_number_or_shelfmark = models.CharField(max_length=500)
    printed_edition_details = models.TextField()
    paper_size = models.CharField(max_length=500)
    paper_type_or_watermark = models.CharField(max_length=500)
    number_of_pages_of_document = models.IntegerField()
    number_of_pages_of_text = models.IntegerField()
    seal = models.CharField(max_length=500)
    postage_marks = models.CharField(max_length=500)
    endorsements = models.TextField()
    non_letter_enclosures = models.TextField()
    manifestation_creation_calendar = models.CharField(max_length=2, null=False, default='U')
    manifestation_creation_date = models.DateField()
    manifestation_creation_date_gregorian = models.DateField()
    manifestation_creation_date_year = models.IntegerField()
    manifestation_creation_date_month = models.IntegerField()
    manifestation_creation_date_day = models.IntegerField()
    manifestation_creation_date_inferred = models.SmallIntegerField(null=False, default=0)
    manifestation_creation_date_uncertain = models.SmallIntegerField(null=False, default=0)
    manifestation_creation_date_approx = models.SmallIntegerField(null=False, default=0)
    manifestation_is_translation = models.SmallIntegerField(null=False, default=0)
    language_of_manifestation = models.CharField(max_length=255)
    address = models.TextField()
    manifestation_incipit = models.TextField()
    manifestation_excipit = models.TextField()
    manifestation_ps = models.TextField()
    creation_timestamp = models.DateTimeField(auto_now=True)
    # TODO
    # All user references in tables seem to refer to database user and NOT
    # system users. This has to be fixed
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    manifestation_creation_date2_year = models.IntegerField()
    manifestation_creation_date2_month = models.IntegerField()
    manifestation_creation_date2_day = models.IntegerField()
    manifestation_creation_date_is_range = models.SmallIntegerField(null=False, default=0)
    manifestation_creation_date_as_marked = models.CharField(max_length=250)
    # Enumerated values?
    # TODO
    opened = models.CharField(max_length=3, null=False, default='o')
    uuid = models.UUIDField(default=uuid.uuid4)
    routing_mark_stamp = models.TextField()
    routing_mark_ms = models.TextField()
    handling_instructions = models.TextField()
    stored_folded = models.CharField(max_length=20)
    postage_costs_as_marked = models.CharField(max_length=500)
    postage_costs = models.CharField(max_length=500)
    non_delivery_reason = models.CharField(max_length=500)
    date_of_receipt_as_marked = models.CharField(max_length=500)
    # Enumerated values?
    # TODO
    manifestation_receipt_calendar = models.CharField(max_length=2, null=False, default='U')
    manifestation_receipt_date = models.DateField()
    manifestation_receipt_date_gregorian = models.DateField()
    manifestation_receipt_date_year = models.IntegerField()
    manifestation_receipt_date_month = models.IntegerField()
    manifestation_receipt_date_day = models.IntegerField()
    manifestation_receipt_date_inferred = models.SmallIntegerField(null=False, default=0)
    manifestation_receipt_date_uncertain = models.SmallIntegerField(null=False, default=0)
    manifestation_receipt_date_approx = models.SmallIntegerField(null=False, default=0)
    manifestation_receipt_date2_year = models.IntegerField()
    manifestation_receipt_date2_month = models.IntegerField()
    manifestation_receipt_date2_day = models.IntegerField()
    manifestation_receipt_date_is_range = models.SmallIntegerField(null=False, default=0)
    accompaniments = models.TextField()


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


class CofkUser(models.Model):
    class Meta:
        db_table = 'cofk_users'

    username = models.CharField(max_length=30, primary_key=True)
    # pw changed from Textfield
    pw = models.CharField(max_length=100, null=False)
    surname = models.CharField(max_length=30, null=False, default='')
    forename = models.CharField(max_length=30, null=False, default='')
    failed_logins = models.IntegerField(null=False, default=0)
    login_time = models.DateTimeField(null=True)
    prev_login = models.DateTimeField(null=True)
    # Active changed to boolean
    # active = models.SmallIntegerField(null=False, default=1)
    active = models.BooleanField(default=True, null=False)
    # Can be changed to email field
    # email = models.TextField()
    email = models.EmailField(null=True)


class Iso639LanguageCode(models.Model):
    class Meta:
        db_table = 'iso_639_language_codes'

    code_639_3 = models.CharField(max_length=3, default='')
    code_639_1 = models.CharField(max_length=2, null=False, default='')
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


class CofkCollectUpload(models.Model):
    class Meta:
        db_table = 'cofk_collect_upload'

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
'''


# TODO
# Composite primary keys

class CofkUnionLanguageOfManifestation(models.Model):
    class Meta:
        db_table = 'cofk_union_language_of_manifestation'

    # manifestation_id = Column(ForeignKey('cofk_union_manifestation.manifestation_id', ondelete='CASCADE'), primary_key=True, null=False)
    # manifestation_id = models.ForeignKey("uploader.CofkUnionManifestation", on_delete=models.CASCADE, primary_key=True)
    manifestation_id = models.OneToOneField("uploader.CofkUnionManifestation", on_delete=models.CASCADE)
    # language_code = Column(ForeignKey('iso_639_language_codes.code_639_3', ondelete='CASCADE'), primary_key=True, null=False)
    # both primary keys?
    language_code = models.ForeignKey("uploader.Iso639LanguageCode", on_delete=models.CASCADE, null=False)
    notes = models.CharField(max_length=100)

    # iso_639_language_code = relationship('Iso639LanguageCode')
    # manifestation = relationship('CofkUnionManifestation')


class CofkUnionPerson(models.Model):
    class Meta:
        db_table = 'cofk_union_person'

    # __table_args__ = (
    #    CheckConstraint('(date_of_birth_approx = 0) OR (date_of_birth_approx = 1)'),
    #    CheckConstraint('(date_of_birth_inferred = 0) OR (date_of_birth_inferred = 1)'),
    #    CheckConstraint('(date_of_birth_is_range = 0) OR (date_of_birth_is_range = 1)'),
    #    CheckConstraint('(date_of_birth_uncertain = 0) OR (date_of_birth_uncertain = 1)'),
    #    CheckConstraint('(date_of_death_approx = 0) OR (date_of_death_approx = 1)'),
    #    CheckConstraint('(date_of_death_inferred = 0) OR (date_of_death_inferred = 1)'),
    #    CheckConstraint('(date_of_death_is_range = 0) OR (date_of_death_is_range = 1)'),
    #    CheckConstraint('(date_of_death_uncertain = 0) OR (date_of_death_uncertain = 1)'),
    #    CheckConstraint('(flourished_is_range = 0) OR (flourished_is_range = 1)')
    # )

    # TODO
    # Switch above to boolean fields

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
    # TODO
    # Enumerated value?
    gender = models.CharField(max_length=1, null=False, default='')
    # TODO
    # Boolean field
    is_organisation = models.CharField(max_length=1, null=False, default='')
    # iperson_id = models.IntegerField(null=False, unique=True, default=text("nextval('cofk_union_person_iperson_id_seq'::regclass)"))
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    editors_notes = models.TextField()
    further_reading = models.TextField()
    # organisation_type = Column(ForeignKey('cofk_union_org_type.org_type_id'))
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
    # TODO
    # Boolean fields below
    flourished_inferred = models.SmallIntegerField(null=False, default=0)
    flourished_uncertain = models.SmallIntegerField(null=False, default=0)
    flourished_approx = models.SmallIntegerField(null=False, default=0)

    # cofk_union_org_type = relationship('CofkUnionOrgType')


'''
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


class CofkUnionWork(models.Model):
    class Meta:
        db_table = 'cofk_union_work'

    '''__table_args__ = (
        CheckConstraint('(addressees_inferred = 0) OR (addressees_inferred = 1)'),
        CheckConstraint('(addressees_uncertain = 0) OR (addressees_uncertain = 1)'),
        CheckConstraint('(authors_inferred = 0) OR (authors_inferred = 1)'),
        CheckConstraint('(authors_uncertain = 0) OR (authors_uncertain = 1)'),
        CheckConstraint('(date_of_work_approx = 0) OR (date_of_work_approx = 1)'),
        CheckConstraint('(date_of_work_inferred = 0) OR (date_of_work_inferred = 1)'),
        CheckConstraint('(date_of_work_std_is_range = 0) OR (date_of_work_std_is_range = 1)'),
        CheckConstraint('(date_of_work_uncertain = 0) OR (date_of_work_uncertain = 1)'),
        CheckConstraint('(destination_inferred = 0) OR (destination_inferred = 1)'),
        CheckConstraint('(destination_uncertain = 0) OR (destination_uncertain = 1)'),
        CheckConstraint('(origin_inferred = 0) OR (origin_inferred = 1)'),
        CheckConstraint('(origin_uncertain = 0) OR (origin_uncertain = 1)'),
        CheckConstraint('(work_is_translation = 0) OR (work_is_translation = 1)'),
        CheckConstraint('(work_to_be_deleted = 0) OR (work_to_be_deleted = 1)')
    )'''

    work_id = models.CharField(max_length=100)  # , primary_key=True)
    description = models.TextField()
    date_of_work_as_marked = models.CharField(max_length=250)
    original_calendar = models.CharField(max_length=2, null=False, default='')
    date_of_work_std = models.CharField(max_length=12)  # , default=text("'9999-12-31'::character varying"))
    date_of_work_std_gregorian = models.CharField(max_length=12)  # , default=text("'9999-12-31'::character varying"))
    date_of_work_std_year = models.IntegerField()
    date_of_work_std_month = models.IntegerField()
    date_of_work_std_day = models.IntegerField()
    date_of_work2_std_year = models.IntegerField()
    date_of_work2_std_month = models.IntegerField()
    date_of_work2_std_day = models.IntegerField()
    # TODO
    # A lot of boolean field below
    date_of_work_std_is_range = models.SmallIntegerField(null=False, default=0)
    date_of_work_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_work_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_work_approx = models.SmallIntegerField(null=False, default=0)
    authors_as_marked = models.TextField()
    addressees_as_marked = models.TextField()
    authors_inferred = models.SmallIntegerField(null=False, default=0)
    authors_uncertain = models.SmallIntegerField(null=False, default=0)
    addressees_inferred = models.SmallIntegerField(null=False, default=0)
    addressees_uncertain = models.SmallIntegerField(null=False, default=0)
    destination_as_marked = models.TextField()
    origin_as_marked = models.TextField()
    destination_inferred = models.SmallIntegerField(null=False, default=0)
    destination_uncertain = models.SmallIntegerField(null=False, default=0)
    origin_inferred = models.SmallIntegerField(null=False, default=0)
    origin_uncertain = models.SmallIntegerField(null=False, default=0)
    abstract = models.TextField()
    keywords = models.TextField()
    language_of_work = models.CharField(max_length=255)
    work_is_translation = models.SmallIntegerField(null=False, default=0)
    incipit = models.TextField()
    explicit = models.TextField()
    ps = models.TextField()
    # TODO on update
    # original_catalogue = Column(ForeignKey('cofk_lookup_catalogue.catalogue_code', onupdate='CASCADE'), null=False, default='')
    # missing onupdate
    original_catalogue = models.ForeignKey("uploader.CofkLookupCatalogue", null=False, default='',
                                           on_delete=models.DO_NOTHING)
    accession_code = models.CharField(max_length=1000)
    work_to_be_deleted = models.SmallIntegerField(null=False, default=0)
    iwork_id = models.AutoField(primary_key=True, null=False, unique=True)
    editors_notes = models.TextField()
    # TODO
    # Enumarated field?
    edit_status = models.CharField(max_length=3, null=False, default='')
    # TODO
    # Boolean field
    relevant_to_cofk = models.CharField(max_length=3, null=False, default='Y')
    creation_timestamp = models.DateTimeField(auto_now=True)
    # creation_user = models.CharField(max_length=50, null=False, default=current_user)
    change_timestamp = models.DateTimeField(auto_now=True)
    # change_user = models.CharField(max_length=50, null=False, default=current_user)
    uuid = models.UUIDField(default=uuid.uuid4)

    # cofk_lookup_catalogue = relationship('CofkLookupCatalogue')


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


class CofkCollectInstitution(models.Model):
    class Meta:
        db_table = 'cofk_collect_institution'

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    institution_id = models.AutoField(primary_key=True)
    # union_institution_id = Column(ForeignKey('cofk_union_institution.institution_id', ondelete='SET NULL'))
    # union_institution_id = models.ForeignKey("uploader.CofkUnionInstitution", on_delete=models.SET_NULL)
    union_institution_id = models.OneToOneField("uploader.CofkUnionInstitution", on_delete=models.DO_NOTHING)
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


class CofkCollectLocation(models.Model):
    class Meta:
        db_table = 'cofk_collect_location'

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    location_id = models.AutoField(primary_key=True)
    # union_location_id = Column(ForeignKey('cofk_union_location.location_id', ondelete='SET NULL'))
    union_location_id = models.ForeignKey("uploader.CofkUnionLocation", on_delete=models.DO_NOTHING)
    location_name = models.CharField(max_length=500, null=False, default='')
    element_1_eg_room = models.CharField(max_length=100, null=False, default='')
    element_2_eg_building = models.CharField(max_length=100, null=False, default='')
    element_3_eg_parish = models.CharField(max_length=100, null=False, default='')
    element_4_eg_city = models.CharField(max_length=100, null=False, default='')
    element_5_eg_county = models.CharField(max_length=100, null=False, default='')
    element_6_eg_country = models.CharField(max_length=100, null=False, default='')
    element_7_eg_empire = models.CharField(max_length=100, null=False, default='')
    notes_on_place = models.TextField()
    editors_notes = models.TextField()
    upload_name = models.CharField(max_length=254)
    _id = models.CharField(max_length=32)
    location_synonyms = models.TextField()
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

    # union_location = relationship('CofkUnionLocation')
    # upload = relationship('CofkCollectUpload')


class CofkCollectPerson(models.Model):
    class Meta:
        db_table = 'cofk_collect_person'

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    # iperson_id = models.AutoField(primary_key=True)
    # union_iperson_id = Column(ForeignKey('cofk_union_person.iperson_id', ondelete='SET NULL'))
    # TODO
    # Union iperson id necessary?
    # union_iperson_id = models.ForeignKey(CofkUnionPerson.i)
    # person_id = Column(ForeignKey('cofk_union_person.person_id', ondelete='SET NULL'))
    person_id = models.OneToOneField("uploader.CofkUnionPerson", on_delete=models.DO_NOTHING)
    primary_name = models.CharField(max_length=200, null=False)
    alternative_names = models.TextField()
    roles_or_titles = models.TextField()
    # TODO
    # Enumerate type?
    gender = models.CharField(max_length=1, null=False, default='')
    # TODO
    # Boolean field
    is_organisation = models.CharField(max_length=1, null=False, default='')
    # TODO
    # Enumerate type?
    organisation_type = models.IntegerField()
    date_of_birth_year = models.IntegerField()
    date_of_birth_month = models.IntegerField()
    date_of_birth_day = models.IntegerField()
    # TODO
    # Boolean types below?
    date_of_birth_is_range = models.SmallIntegerField(null=False, default=0)
    date_of_birth2_year = models.IntegerField()
    date_of_birth2_month = models.IntegerField()
    date_of_birth2_day = models.IntegerField()
    date_of_birth_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_birth_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_birth_approx = models.SmallIntegerField(null=False, default=0)
    date_of_death_year = models.IntegerField()
    date_of_death_month = models.IntegerField()
    date_of_death_day = models.IntegerField()
    date_of_death_is_range = models.SmallIntegerField(null=False, default=0)
    date_of_death2_year = models.IntegerField()
    date_of_death2_month = models.IntegerField()
    date_of_death2_day = models.IntegerField()
    date_of_death_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_death_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_death_approx = models.SmallIntegerField(null=False, default=0)
    flourished_year = models.IntegerField()
    flourished_month = models.IntegerField()
    flourished_day = models.IntegerField()
    flourished_is_range = models.SmallIntegerField(null=False, default=0)
    flourished2_year = models.IntegerField()
    flourished2_month = models.IntegerField()
    flourished2_day = models.IntegerField()
    notes_on_person = models.TextField()
    editors_notes = models.TextField()
    # TODO
    # What does upload name refer to here?
    upload_name = models.CharField(max_length=254)
    _id = models.CharField(max_length=32)

    # person = relationship('CofkUnionPerson', primaryjoin='CofkCollectPerson.person_id == CofkUnionPerson.person_id')
    # union_iperson = relationship('CofkUnionPerson', primaryjoin='CofkCollectPerson.union_iperson_id == CofkUnionPerson.iperson_id')
    # upload = relationship('CofkCollectUpload')


class CofkUnionLanguageOfWork(models.Model):
    class Meta:
        db_table = 'cofk_union_language_of_work'

    # TODO
    # Composite primary keys

    # work_id = Column(ForeignKey('cofk_union_work.work_id', ondelete='CASCADE'), primary_key=True, null=False)
    # work_id = models.ForeignKey("uploader.CofkUnionWork", on_delete=models.CASCADE, primary_key=True, null=False)
    work_id = models.OneToOneField("uploader.CofkUnionWork", on_delete=models.CASCADE, null=False)
    # language_code = Column(ForeignKey('iso_639_language_codes.code_639_3', ondelete='CASCADE'), primary_key=True, null=False)
    # missing 2x primary key
    language_code = models.ForeignKey("uploader.Iso639LanguageCode", on_delete=models.CASCADE, null=False)
    notes = models.CharField(max_length=100)

    # iso_639_language_code = relationship('Iso639LanguageCode')
    # work = relationship('CofkUnionWork')


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


class CofkCollectInstitutionResource(models.Model):
    class Meta:
        db_table = 'cofk_collect_institution_resource'

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


class CofkCollectLocationResource(models.Model):
    class Meta:
        db_table = 'cofk_collect_location_resource'

    # __table_args__ = (
    #    ForeignKeyConstraint(['upload_id', 'location_id'], ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id']),
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    resource_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')

    # upload = relationship('CofkCollectLocation')
    # upload1 = relationship('CofkCollectUpload')


class CofkCollectOccupationOfPerson(models.Model):
    class Meta:
        db_table = 'cofk_collect_occupation_of_person'

    # __table_args__ = (
    #    ForeignKeyConstraint(['upload_id', 'iperson_id'], ['cofk_collect_person.upload_id', 'cofk_collect_person.iperson_id']),
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    occupation_of_person_id = models.AutoField(primary_key=True)
    iperson_id = models.IntegerField(null=False)
    occupation_id = models.ForeignKey("uploader.CofkUnionRoleCategory", on_delete=models.CASCADE, null=False)
    # occupation_id = Column(ForeignKey('cofk_union_role_category.role_category_id', ondelete='CASCADE'), null=False)

    # occupation = relationship('CofkUnionRoleCategory')
    # upload = relationship('CofkCollectPerson')
    # upload1 = relationship('CofkCollectUpload')


class CofkCollectPersonResource(models.Model):
    class Meta:
        db_table = 'cofk_collect_person_resource'

    # __table_args__ = (
    #    ForeignKeyConstraint(['upload_id', 'iperson_id'], ['cofk_collect_person.upload_id', 'cofk_collect_person.iperson_id']),
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    resource_id = models.AutoField(primary_key=True, null=False)
    iperson_id = models.IntegerField(null=False)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')

    # upload = relationship('CofkCollectPerson')
    # upload1 = relationship('CofkCollectUpload')


class CofkCollectWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_work'

    __table_args__ = (
        #    ForeignKeyConstraint(['upload_id', 'destination_id'], ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id']),
        #    ForeignKeyConstraint(['upload_id', 'origin_id'], ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id'])
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    iwork_id = models.AutoField(primary_key=True)
    union_iwork_id = models.ForeignKey("uploader.CofkUnionWork", on_delete=models.DO_NOTHING)
    # union_iwork_id = Column(ForeignKey('cofk_union_work.iwork_id', ondelete='SET NULL'))
    # work_id = Column(ForeignKey('cofk_union_work.work_id', ondelete='SET NULL'))
    # work_id = models.ForeignKey("uploader.CofkUnionWork", on_delete=models.SET_NULL)
    # TODO
    # Missing work_id
    date_of_work_as_marked = models.CharField(max_length=250)
    original_calendar = models.CharField(max_length=2, null=False, default='')
    date_of_work_std_year = models.IntegerField()
    date_of_work_std_month = models.IntegerField()
    date_of_work_std_day = models.IntegerField()
    date_of_work2_std_year = models.IntegerField()
    date_of_work2_std_month = models.IntegerField()
    date_of_work2_std_day = models.IntegerField()
    # TODO
    # Booleans below
    date_of_work_std_is_range = models.SmallIntegerField(null=False, default=0)
    date_of_work_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_work_uncertain = models.SmallIntegerField(null=False, default=0)
    date_of_work_approx = models.SmallIntegerField(null=False, default=0)
    notes_on_date_of_work = models.TextField()
    authors_as_marked = models.TextField()
    authors_inferred = models.SmallIntegerField(null=False, default=0)
    authors_uncertain = models.SmallIntegerField(null=False, default=0)
    notes_on_authors = models.TextField()
    addressees_as_marked = models.TextField()
    addressees_inferred = models.SmallIntegerField(null=False, default=0)
    addressees_uncertain = models.SmallIntegerField(null=False, default=0)
    notes_on_addressees = models.TextField()
    destination_id = models.IntegerField()
    destination_as_marked = models.TextField()
    destination_inferred = models.SmallIntegerField(null=False, default=0)
    destination_uncertain = models.SmallIntegerField(null=False, default=0)
    origin_id = models.IntegerField()
    origin_as_marked = models.TextField()
    origin_inferred = models.SmallIntegerField(null=False, default=0)
    origin_uncertain = models.SmallIntegerField(null=False, default=0)
    abstract = models.TextField()
    keywords = models.TextField()
    language_of_work = models.CharField(max_length=255)
    incipit = models.TextField()
    excipit = models.TextField()
    accession_code = models.CharField(max_length=250)
    notes_on_letter = models.TextField()
    notes_on_people_mentioned = models.TextField()
    # upload_status = Column(ForeignKey('cofk_collect_status.status_id'), null=False, default=text("1"))
    upload_status = models.ForeignKey("uploader.CofkCollectStatus", null=False, default="1",
                                      on_delete=models.DO_NOTHING)
    editors_notes = models.TextField()
    _id = models.CharField(max_length=32)
    date_of_work2_approx = models.SmallIntegerField(null=False, default=0)
    date_of_work2_inferred = models.SmallIntegerField(null=False, default=0)
    date_of_work2_uncertain = models.SmallIntegerField(null=False, default=0)
    mentioned_as_marked = models.TextField()
    mentioned_inferred = models.SmallIntegerField(null=False, default=0)
    mentioned_uncertain = models.SmallIntegerField(null=False, default=0)
    notes_on_destination = models.TextField()
    notes_on_origin = models.TextField()
    notes_on_place_mentioned = models.TextField()
    place_mentioned_as_marked = models.TextField()
    place_mentioned_inferred = models.SmallIntegerField(null=False, default=0)
    place_mentioned_uncertain = models.SmallIntegerField(null=False, default=0)
    upload_name = models.CharField(max_length=254)
    explicit = models.TextField()

    # union_iwork = relationship('CofkUnionWork', primaryjoin='CofkCollectWork.union_iwork_id == CofkUnionWork.iwork_id')
    # upload = relationship('CofkCollectLocation', primaryjoin='CofkCollectWork.upload_id == CofkCollectLocation.upload_id')
    # upload1 = relationship('CofkCollectLocation', primaryjoin='CofkCollectWork.upload_id == CofkCollectLocation.upload_id')
    # upload2 = relationship('CofkCollectUpload')
    # cofk_collect_statu = relationship('CofkCollectStatus')
    # work = relationship('CofkUnionWork', primaryjoin='CofkCollectWork.work_id == CofkUnionWork.work_id')


'''
class CofkCollectWorkSummary(CofkCollectWork):
    class Meta:
        db_table = 'cofk_collect_work_summary'

    __table_args__ = (
        #    ForeignKeyConstraint(['upload_id', 'work_id_in_tool'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
    )

    # upload_id = models.AutoField(primary_key=True)
    # work_id_in_tool = models.AutoField(primary_key=True)
    source_of_data = models.CharField(max_length=250)
    # notes_on_letter = models.TextField()
    date_of_work = models.CharField(max_length=32)
    # date_of_work_as_marked = models.CharField(max_length=250)
    # original_calendar = models.CharField(max_length=30)
    date_of_work_is_range = models.CharField(max_length=30)
    # date_of_work_inferred = models.CharField(max_length=30)
    # date_of_work_uncertain = models.CharField(max_length=30)
    # date_of_work_approx = models.CharField(max_length=30)
    # notes_on_date_of_work = models.TextField()
    authors = models.TextField()
    # authors_as_marked = models.TextField()
    # authors_inferred = models.CharField(max_length=30)
    # authors_uncertain = models.CharField(max_length=30)
    # notes_on_authors = models.TextField()
    addressees = models.TextField()
    # addressees_as_marked = models.TextField()
    # addressees_inferred = models.CharField(max_length=30)
    # addressees_uncertain = models.CharField(max_length=30)
    # notes_on_addressees = models.TextField()
    destination = models.TextField()
    # destination_as_marked = models.TextField()
    # destination_inferred = models.CharField(max_length=30)
    # destination_uncertain = models.CharField(max_length=30)
    origin = models.TextField()
    # origin_as_marked = models.TextField()
    # origin_inferred = models.CharField(max_length=30)
    # origin_uncertain = models.CharField(max_length=30)
    # abstract = models.TextField()
    # keywords = models.TextField()
    languages_of_work = models.TextField()
    subjects_of_work = models.TextField()
    # incipit = models.TextField()
    # excipit = models.TextField()
    people_mentioned = models.TextField()
    # notes_on_people_mentioned = models.TextField()
    places_mentioned = models.TextField()
    manifestations = models.TextField()
    related_resources = models.TextField()
    # editors_notes = models.TextField()
'''


class CofkCollectAddresseeOfWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_addressee_of_work'

    # __table_args__ = (
    # ForeignKeyConstraint(['upload_id', 'iperson_id'], ['cofk_collect_person.upload_id', 'cofk_collect_person.iperson_id']),
    # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id'])
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    addressee_id = models.AutoField(primary_key=True)
    # TODO
    # Fix missing columns below
    # iperson_id = models.IntegerField(null=False)
    # iwork_id = models.AutoField(primary_key=True)
    notes_on_addressee = models.TextField()
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectPerson')
    # upload1 = relationship('CofkCollectWork')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectAuthorOfWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_author_of_work'

    # __table_args__ = (
    # ForeignKeyConstraint(['upload_id', 'iperson_id'], ['cofk_collect_person.upload_id', 'cofk_collect_person.iperson_id']),
    # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id'])
    # )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    author_id = models.AutoField(primary_key=True)
    iperson_id = models.IntegerField(null=False)
    # TODO
    # missing iwork_id
    # iwork_id = models.AutoField(primary_key=True)
    notes_on_author = models.TextField()
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectPerson')
    # upload1 = relationship('CofkCollectWork')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectDestinationOfWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_destination_of_work'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
        # ForeignKeyConstraint(['upload_id', 'location_id'], ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id'])
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    destination_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    # TODO
    # missing iwork_id
    # iwork_id = models.AutoField(primary_key=True)
    notes_on_destination = models.TextField()
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectLocation')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectLanguageOfWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_language_of_work'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    language_of_work_id = models.AutoField(primary_key=True)
    # TODO
    # missing iwork_id
    # iwork_id = models.AutoField(primary_key=True)
    # language_code = Column(ForeignKey('iso_639_language_codes.code_639_3'), null=False)
    language_code = models.ForeignKey("uploader.Iso639LanguageCode", null=False, on_delete=models.DO_NOTHING)
    _id = models.CharField(max_length=32)

    # iso_639_language_code = relationship('Iso639LanguageCode')
    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectUpload')


class CofkCollectManifestation(models.Model):
    class Meta:
        db_table = 'cofk_collect_manifestation'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
        # ForeignKeyConstraint(['upload_id', 'repository_id'], ['cofk_collect_institution.upload_id', 'cofk_collect_institution.institution_id'])
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    manifestation_id = models.AutoField(primary_key=True)
    # TODO
    # missing iwork_id
    # iwork_id = models.AutoField(primary_key=True)
    # union_manifestation_id = Column(ForeignKey('cofk_union_manifestation.manifestation_id', ondelete='SET NULL'))
    # union_manifestation_id = models.ForeignKey("uploader.CofkUnionManifestation", on_delete=models.SET_NULL)
    union_manifestation_id = models.OneToOneField("uploader.CofkUnionManifestation", on_delete=models.DO_NOTHING)
    # TODO
    # Enumerate field?
    manifestation_type = models.CharField(max_length=3, null=False, default='')
    repository_id = models.IntegerField()
    id_number_or_shelfmark = models.CharField(max_length=500)
    printed_edition_details = models.TextField()
    manifestation_notes = models.TextField()
    # TODO
    # Appropriate free text fields below?
    image_filenames = models.TextField()
    upload_name = models.CharField(max_length=254)
    _id = models.CharField(max_length=32)

    # union_manifestation = relationship('CofkUnionManifestation')
    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectInstitution')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectOriginOfWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_origin_of_work'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
        # ForeignKeyConstraint(['upload_id', 'location_id'], ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id'])
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", on_delete=models.DO_NOTHING)
    origin_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    # TODO
    # missing iwork_id
    # iwork_id = models.AutoField(primary_key=True)
    notes_on_origin = models.TextField()
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectLocation')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectPersonMentionedInWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_person_mentioned_in_work'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iperson_id'], ['cofk_collect_person.upload_id', 'cofk_collect_person.iperson_id']),
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id'])
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    # mention_id = models.AutoField(primary_key=True)
    iperson_id = models.IntegerField(null=False)
    # TODO
    # missing iwork_id
    # iwork_id = models.AutoField(primary_key=True)
    notes_on_person_mentioned = models.TextField()
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectPerson')
    # upload1 = relationship('CofkCollectWork')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectPlaceMentionedInWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_place_mentioned_in_work'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id',
        # 'cofk_collect_work.iwork_id']), ForeignKeyConstraint(['upload_id', 'location_id'],
        # ['cofk_collect_location.upload_id', 'cofk_collect_location.location_id'])
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False) upload_id =
    # models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    # mention_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    # iwork_id = models.AutoField(primary_key=True)
    notes_on_place_mentioned = models.TextField()
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectLocation')
    # upload2 = relationship('CofkCollectUpload')


class CofkCollectSubjectOfWork(models.Model):
    class Meta:
        db_table = 'cofk_collect_subject_of_work'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    subject_of_work_id = models.AutoField(primary_key=True)
    # iwork_id = models.AutoField(primary_key=True)
    # subject_id = Column(ForeignKey('cofk_union_subject.subject_id', ondelete='CASCADE'), null=False)
    subject_id = models.ForeignKey("uploader.CofkUnionSubject", on_delete=models.CASCADE, null=False)

    # subject = relationship('CofkUnionSubject')
    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectUpload')


class CofkCollectWorkResource(models.Model):
    class Meta:
        db_table = 'cofk_collect_work_resource'

    __table_args__ = (
        # ForeignKeyConstraint(['upload_id', 'iwork_id'], ['cofk_collect_work.upload_id', 'cofk_collect_work.iwork_id']),
    )

    # upload_id = Column(ForeignKey('cofk_collect_upload.upload_id'), primary_key=True, null=False)
    # upload_id = models.ForeignKey("uploader.CofkCollectUpload", primary_key=True, null=False, on_delete=models.DO_NOTHING)
    upload_id = models.OneToOneField("uploader.CofkCollectUpload", null=False, on_delete=models.DO_NOTHING)
    # resource_id = models.AutoField(primary_key=True)
    # iwork_id = models.AutoField(primary_key=True)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')
    _id = models.CharField(max_length=32)

    # upload = relationship('CofkCollectWork')
    # upload1 = relationship('CofkCollectUpload')
