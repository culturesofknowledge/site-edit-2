# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CofkCollectImageOfManif(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.DO_NOTHING)
    manifestation_id = models.IntegerField()
    image_filename = models.CharField(max_length=2000)
    _id = models.CharField(max_length=32, blank=True, null=True)
    iwork_id = models.IntegerField(blank=True, null=True)



class CofkCollectToolSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    session_timestamp = models.DateTimeField()
    session_code = models.TextField(unique=True, blank=True, null=True)
    username = models.ForeignKey('CofkCollectToolUser', models.DO_NOTHING, db_column='username', blank=True, null=True)

    

class CofkHelpOptions(models.Model):
    option_id = models.AutoField(primary_key=True)
    menu_item = models.ForeignKey('CofkMenu', models.DO_NOTHING, blank=True, null=True)
    button_name = models.CharField(max_length=100)
    help_page = models.ForeignKey('CofkHelpPages', models.DO_NOTHING)
    order_in_manual = models.IntegerField()
    menu_depth = models.IntegerField()

    class Meta:
        db_table = 'cofk_help_options'
        unique_together = (('menu_item', 'button_name'),)


class CofkHelpPages(models.Model):
    page_id = models.AutoField(primary_key=True)
    page_title = models.CharField(max_length=500)
    custom_url = models.CharField(max_length=500, blank=True, null=True)
    published_text = models.TextField()
    draft_text = models.TextField(blank=True, null=True)

    

class CofkLookupDocumentType(models.Model):
    document_type_id = models.AutoField(primary_key=True)
    document_type_code = models.CharField(unique=True, max_length=3)
    document_type_desc = models.CharField(max_length=100)

    

class CofkMenu(models.Model):
    menu_item_id = models.AutoField(primary_key=True)
    menu_item_name = models.TextField()
    menu_order = models.AutoField(blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    has_children = models.IntegerField()
    class_name = models.CharField(max_length=100, blank=True, null=True)
    method_name = models.CharField(max_length=100, blank=True, null=True)
    user_restriction = models.CharField(max_length=30)
    hidden_parent = models.IntegerField(blank=True, null=True)
    called_as_popup = models.IntegerField()
    collection = models.CharField(max_length=20)

    

class CofkReportOutputs(models.Model):
    output_id = models.CharField(max_length=250)
    line_number = models.IntegerField()
    line_text = models.TextField(blank=True, null=True)

    

class CofkUnionComment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)

    

class CofkUnionFavouriteLanguage(models.Model):
    language_code = models.OneToOneField('Iso639LanguageCodes', models.DO_NOTHING, db_column='language_code',
                                         primary_key=True)

    

class CofkUnionNationality(models.Model):
    nationality_id = models.AutoField(primary_key=True)
    nationality_desc = models.CharField(max_length=100)

    

class CofkUnionRelationship(models.Model):
    relationship_id = models.AutoField(primary_key=True)
    left_table_name = models.CharField(max_length=100)
    left_id_value = models.CharField(max_length=100)
    relationship_type = models.ForeignKey('CofkUnionRelationshipType', models.DO_NOTHING, db_column='relationship_type')
    right_table_name = models.CharField(max_length=100)
    right_id_value = models.CharField(max_length=100)
    relationship_valid_from = models.DateTimeField(blank=True, null=True)
    relationship_valid_till = models.DateTimeField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50)

    

class CofkUnionRelationshipType(models.Model):
    relationship_code = models.CharField(primary_key=True, max_length=50)
    desc_left_to_right = models.CharField(max_length=200)
    desc_right_to_left = models.CharField(max_length=200)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50)

    

class CofkUnionResource(models.Model):
    resource_id = models.AutoField(primary_key=True)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)

    

class CofkUnionSpeedEntryText(models.Model):
    speed_entry_text_id = models.AutoField(primary_key=True)
    object_type = models.CharField(max_length=30)
    speed_entry_text = models.CharField(max_length=200)

    

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
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50, blank=True, null=True)
    drawer = models.CharField(max_length=50, blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    manifestation_type = models.CharField(max_length=50, blank=True, null=True)
    original_notes = models.TextField(blank=True, null=True)
    relevant_to_cofk = models.CharField(max_length=1, blank=True, null=True)
    subjects = models.TextField(blank=True, null=True)

    

class ProActivity(models.Model):
    activity_type_id = models.TextField(blank=True, null=True)
    activity_name = models.TextField(blank=True, null=True)
    activity_description = models.TextField(blank=True, null=True)
    date_type = models.TextField(blank=True, null=True)
    date_from_year = models.TextField(blank=True, null=True)
    date_from_month = models.TextField(blank=True, null=True)
    date_from_day = models.TextField(blank=True, null=True)
    date_from_uncertainty = models.TextField(blank=True, null=True)
    date_to_year = models.TextField(blank=True, null=True)
    date_to_month = models.TextField(blank=True, null=True)
    date_to_day = models.TextField(blank=True, null=True)
    date_to_uncertainty = models.TextField(blank=True, null=True)
    notes_used = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.TextField(blank=True, null=True)
    event_label = models.TextField(blank=True, null=True)

    

class ProActivityRelation(models.Model):
    meta_activity_id = models.IntegerField(blank=True, null=True)
    filename = models.TextField()
    spreadsheet_row = models.IntegerField()
    combined_spreadsheet_row = models.IntegerField()

    

class ProAssertion(models.Model):
    assertion_type = models.TextField(blank=True, null=True)
    assertion_id = models.TextField(blank=True, null=True)
    source_id = models.TextField(blank=True, null=True)
    source_description = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)

    

class ProIngestMapV2(models.Model):
    relationship = models.TextField(blank=True, null=True)
    mapping = models.TextField(blank=True, null=True)
    s_event_category = models.TextField(blank=True, null=True)
    s_event_type = models.TextField(blank=True, null=True)
    s_role = models.TextField(blank=True, null=True)
    p_event_category = models.TextField(blank=True, null=True)
    p_event_type = models.TextField(blank=True, null=True)
    p_role = models.TextField(blank=True, null=True)

    

class ProIngestV8(models.Model):
    event_category = models.TextField(blank=True, null=True)
    event_type = models.TextField(blank=True, null=True)
    event_name = models.TextField(blank=True, null=True)
    pp_i = models.TextField(blank=True, null=True)
    pp_name = models.TextField(blank=True, null=True)
    pp_role = models.TextField(blank=True, null=True)
    sp_i = models.TextField(blank=True, null=True)
    sp_name = models.TextField(blank=True, null=True)
    sp_type = models.TextField(blank=True, null=True)
    sp_role = models.TextField(blank=True, null=True)
    df_year = models.TextField(blank=True, null=True)
    df_month = models.TextField(blank=True, null=True)
    df_day = models.TextField(blank=True, null=True)
    df_uncertainty = models.TextField(blank=True, null=True)
    dt_year = models.TextField(blank=True, null=True)
    dt_month = models.TextField(blank=True, null=True)
    dt_day = models.TextField(blank=True, null=True)
    dt_uncertainty = models.TextField(blank=True, null=True)
    date_type = models.TextField(blank=True, null=True)
    location_i = models.TextField(blank=True, null=True)
    location_detail = models.TextField(blank=True, null=True)
    location_city = models.TextField(blank=True, null=True)
    location_region = models.TextField(blank=True, null=True)
    location_country = models.TextField(blank=True, null=True)
    location_type = models.TextField(blank=True, null=True)
    ts_abbrev = models.TextField(blank=True, null=True)
    ts_detail = models.TextField(blank=True, null=True)
    editor = models.TextField(blank=True, null=True)
    noted_used = models.TextField(blank=True, null=True)
    add_notes = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    spreadsheet_row_id = models.TextField(blank=True, null=True)
    combined_csv_row_id = models.TextField(blank=True, null=True)

    

class ProIngestV8Toreview(models.Model):
    event_category = models.TextField(blank=True, null=True)
    event_type = models.TextField(blank=True, null=True)
    event_name = models.TextField(blank=True, null=True)
    pp_i = models.TextField(blank=True, null=True)
    pp_name = models.TextField(blank=True, null=True)
    pp_role = models.TextField(blank=True, null=True)
    sp_i = models.TextField(blank=True, null=True)
    sp_name = models.TextField(blank=True, null=True)
    sp_type = models.TextField(blank=True, null=True)
    sp_role = models.TextField(blank=True, null=True)
    df_year = models.TextField(blank=True, null=True)
    df_month = models.TextField(blank=True, null=True)
    df_day = models.TextField(blank=True, null=True)
    df_uncertainty = models.TextField(blank=True, null=True)
    dt_year = models.TextField(blank=True, null=True)
    dt_month = models.TextField(blank=True, null=True)
    dt_day = models.TextField(blank=True, null=True)
    dt_uncertainty = models.TextField(blank=True, null=True)
    date_type = models.TextField(blank=True, null=True)
    location_i = models.TextField(blank=True, null=True)
    location_detail = models.TextField(blank=True, null=True)
    location_city = models.TextField(blank=True, null=True)
    location_region = models.TextField(blank=True, null=True)
    location_country = models.TextField(blank=True, null=True)
    location_type = models.TextField(blank=True, null=True)
    ts_abbrev = models.TextField(blank=True, null=True)
    ts_detail = models.TextField(blank=True, null=True)
    editor = models.TextField(blank=True, null=True)
    noted_used = models.TextField(blank=True, null=True)
    add_notes = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    spreadsheet_row_id = models.TextField(blank=True, null=True)
    combined_csv_row_id = models.TextField(blank=True, null=True)

    

class ProLocation(models.Model):
    location_id = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    activity_id = models.IntegerField(blank=True, null=True)

    

class ProPeopleCheck(models.Model):
    person_name = models.TextField(blank=True, null=True)
    iperson_id = models.TextField(blank=True, null=True)

    

class ProPrimaryPerson(models.Model):
    person_id = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    activity_id = models.IntegerField(blank=True, null=True)

    

class ProRelationship(models.Model):
    subject_id = models.TextField(blank=True, null=True)
    subject_type = models.TextField(blank=True, null=True)
    subject_role_id = models.TextField(blank=True, null=True)
    relationship_id = models.TextField(blank=True, null=True)
    object_id = models.TextField(blank=True, null=True)
    object_type = models.TextField(blank=True, null=True)
    object_role_id = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    activity_id = models.IntegerField(blank=True, null=True)

    

class ProRoleInActivity(models.Model):
    entity_type = models.TextField(blank=True, null=True)
    entity_id = models.TextField(blank=True, null=True)
    role_id = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    activity_id = models.IntegerField(blank=True, null=True)

    

class ProTextualSource(models.Model):
    author = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    chapterarticletitle = models.TextField(db_column='chapterArticleTitle', blank=True,
                                           null=True)  # Field name made lowercase.
    volumeseriesnumber = models.TextField(db_column='volumeSeriesNumber', blank=True,
                                          null=True)  # Field name made lowercase.
    issuenumber = models.TextField(db_column='issueNumber', blank=True, null=True)  # Field name made lowercase.
    pagenumber = models.TextField(db_column='pageNumber', blank=True, null=True)  # Field name made lowercase.
    editor = models.TextField(blank=True, null=True)
    placepublication = models.TextField(db_column='placePublication', blank=True,
                                        null=True)  # Field name made lowercase.
    datepublication = models.TextField(db_column='datePublication', blank=True, null=True)  # Field name made lowercase.
    urlresource = models.TextField(db_column='urlResource', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.TextField(blank=True, null=True)
    fullbibliographicdetails = models.TextField(db_column='fullBibliographicDetails', blank=True,
                                                null=True)  # Field name made lowercase.
    edition = models.TextField(blank=True, null=True)
    reprintfacsimile = models.TextField(db_column='reprintFacsimile', blank=True,
                                        null=True)  # Field name made lowercase.
    repository = models.TextField(blank=True, null=True)
    creation_user = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.TextField(blank=True, null=True)
    change_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'pro_textual_source'
