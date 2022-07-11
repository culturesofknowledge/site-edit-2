from django.db import models


class CofkUnionWork(models.Model):
    work_id = models.CharField(primary_key=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=2)
    date_of_work_std = models.CharField(max_length=12, blank=True, null=True)
    date_of_work_std_gregorian = models.CharField(max_length=12, blank=True, null=True)
    date_of_work_std_year = models.IntegerField(blank=True, null=True)
    date_of_work_std_month = models.IntegerField(blank=True, null=True)
    date_of_work_std_day = models.IntegerField(blank=True, null=True)
    date_of_work2_std_year = models.IntegerField(blank=True, null=True)
    date_of_work2_std_month = models.IntegerField(blank=True, null=True)
    date_of_work2_std_day = models.IntegerField(blank=True, null=True)
    date_of_work_std_is_range = models.SmallIntegerField()
    date_of_work_inferred = models.SmallIntegerField()
    date_of_work_uncertain = models.SmallIntegerField()
    date_of_work_approx = models.SmallIntegerField()
    authors_as_marked = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    authors_inferred = models.SmallIntegerField()
    authors_uncertain = models.SmallIntegerField()
    addressees_inferred = models.SmallIntegerField()
    addressees_uncertain = models.SmallIntegerField()
    destination_as_marked = models.TextField(blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.SmallIntegerField()
    destination_uncertain = models.SmallIntegerField()
    origin_inferred = models.SmallIntegerField()
    origin_uncertain = models.SmallIntegerField()
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    work_is_translation = models.SmallIntegerField()
    incipit = models.TextField(blank=True, null=True)
    explicit = models.TextField(blank=True, null=True)
    ps = models.TextField(blank=True, null=True)
    original_catalogue = models.ForeignKey("uploader.CofkLookupCatalogue", models.DO_NOTHING,
                                           db_column='original_catalogue')
    accession_code = models.CharField(max_length=1000, blank=True, null=True)
    work_to_be_deleted = models.SmallIntegerField()
    iwork_id = models.AutoField(unique=True)
    editors_notes = models.TextField(blank=True, null=True)
    edit_status = models.CharField(max_length=3)
    relevant_to_cofk = models.CharField(max_length=3)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True)


class CofkCollectWork(models.Model):
    upload = models.OneToOneField("uploader.CofkCollectUpload", models.DO_NOTHING, primary_key=True)
    iwork_id = models.IntegerField()
    union_iwork = models.ForeignKey(CofkUnionWork, models.DO_NOTHING, blank=True, null=True)
    work = models.ForeignKey(CofkUnionWork, models.DO_NOTHING, blank=True, null=True)
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=2)
    date_of_work_std_year = models.IntegerField(blank=True, null=True)
    date_of_work_std_month = models.IntegerField(blank=True, null=True)
    date_of_work_std_day = models.IntegerField(blank=True, null=True)
    date_of_work2_std_year = models.IntegerField(blank=True, null=True)
    date_of_work2_std_month = models.IntegerField(blank=True, null=True)
    date_of_work2_std_day = models.IntegerField(blank=True, null=True)
    date_of_work_std_is_range = models.BooleanField(null=True, default=False)
    date_of_work_inferred = models.BooleanField(null=True, default=False)
    date_of_work_uncertain = models.BooleanField(null=True, default=False)
    date_of_work_approx = models.BooleanField(null=True, default=False)
    notes_on_date_of_work = models.TextField(blank=True, null=True)
    authors_as_marked = models.TextField(blank=True, null=True)
    authors_inferred = models.BooleanField(null=True, default=False)
    authors_uncertain = models.BooleanField(null=True, default=False)
    notes_on_authors = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    addressees_inferred = models.BooleanField(null=True, default=False)
    addressees_uncertain = models.BooleanField(null=True, default=False)
    notes_on_addressees = models.TextField(blank=True, null=True)
    destination_id = models.IntegerField(blank=True, null=True)
    destination_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.BooleanField(null=True, default=False)
    destination_uncertain = models.BooleanField(null=True, default=False)
    origin_id = models.IntegerField(blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    origin_inferred = models.BooleanField(null=True, default=False)
    origin_uncertain = models.BooleanField(null=True, default=False)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    incipit = models.TextField(blank=True, null=True)
    excipit = models.TextField(blank=True, null=True)
    accession_code = models.CharField(max_length=250, blank=True, null=True)
    notes_on_letter = models.TextField(blank=True, null=True)
    notes_on_people_mentioned = models.TextField(blank=True, null=True)
    upload_status = models.ForeignKey("uploader.CofkCollectStatus", models.DO_NOTHING, db_column='upload_status')
    editors_notes = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)
    date_of_work2_approx = models.BooleanField(null=True, default=False)
    date_of_work2_inferred = models.BooleanField(null=True, default=False)
    date_of_work2_uncertain = models.BooleanField(null=True, default=False)
    mentioned_as_marked = models.TextField(blank=True, null=True)
    mentioned_inferred = models.SmallIntegerField()
    mentioned_uncertain = models.SmallIntegerField()
    notes_on_destination = models.TextField(blank=True, null=True)
    notes_on_origin = models.TextField(blank=True, null=True)
    notes_on_place_mentioned = models.TextField(blank=True, null=True)
    place_mentioned_as_marked = models.TextField(blank=True, null=True)
    place_mentioned_inferred = models.SmallIntegerField()
    place_mentioned_uncertain = models.SmallIntegerField()
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    explicit = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_work'
        unique_together = (('upload', 'iwork_id'),)


class CofkCollectAddresseeOfWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", on_delete=models.CASCADE, null=False)
    addressee_id = models.IntegerField(null=False)
    iperson_id = models.IntegerField(null=False)
    iwork_id = models.IntegerField(null=False)
    notes_on_addressee = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_addressee_of_work'
        unique_together = (('upload', 'iwork_id', 'addressee_id'),)


class CofkCollectAuthorOfWork(models.Model):
    upload_ = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    author_id = models.IntegerField(null=False)
    iperson_id = models.IntegerField(null=False)
    iwork_id = models.IntegerField(null=False)
    notes_on_author = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_author_of_work'
        unique_together = (('upload', 'iwork_id', 'author_id'),)


class CofkCollectDestinationOfWork(models.Model):
    upload_ = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    destination_id = models.IntegerField(null=False)
    location_id = models.IntegerField(null=False)
    iwork_id = models.IntegerField(null=False)
    notes_on_destination = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_destination_of_work'
        unique_together = (('upload', 'iwork_id', 'destination_id'),)


class CofkCollectLanguageOfWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    language_of_work_id = models.IntegerField()
    iwork_id = models.IntegerField()
    language_code = models.ForeignKey('Iso639LanguageCodes', models.DO_NOTHING, db_column='language_code')
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_language_of_work'
        unique_together = (('upload', 'iwork_id', 'language_of_work_id'),)


class CofkCollectOriginOfWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    origin_id = models.IntegerField()
    location_id = models.IntegerField()
    iwork_id = models.IntegerField()
    notes_on_origin = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_origin_of_work'
        unique_together = (('upload', 'iwork_id', 'origin_id'),)


class CofkCollectPersonMentionedInWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    mention_id = models.IntegerField()
    iperson_id = models.IntegerField()
    iwork_id = models.IntegerField()
    notes_on_person_mentioned = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_person_mentioned_in_work'
        unique_together = (('upload', 'iwork_id', 'mention_id'),)


class CofkCollectPlaceMentionedInWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    mention_id = models.IntegerField()
    location_id = models.IntegerField()
    iwork_id = models.IntegerField()
    notes_on_place_mentioned = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_place_mentioned_in_work'
        unique_together = (('upload', 'iwork_id', 'mention_id'),)


class CofkCollectSubjectOfWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    subject_of_work_id = models.IntegerField()
    iwork_id = models.IntegerField()
    subject = models.ForeignKey('CofkUnionSubject', models.DO_NOTHING)

    class Meta:
        db_table = 'cofk_collect_subject_of_work'
        unique_together = (('upload', 'iwork_id', 'subject_of_work_id'),)


class CofkCollectWorkResource(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    resource_id = models.IntegerField()
    iwork_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()
    _id = models.CharField(max_length=32)

    class Meta:
        db_table = 'cofk_collect_work_resource'
        unique_together = (('upload', 'iwork_id', 'resource_id'),)


class CofkUnionLanguageOfWork(models.Model):
    work = models.OneToOneField('CofkUnionWork', models.DO_NOTHING, primary_key=True)
    language_code = models.ForeignKey('Iso639LanguageCodes', models.DO_NOTHING, db_column='language_code')
    notes = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_language_of_work'
        unique_together = (('work', 'language_code'),)


class CofkUnionQueryableWork(models.Model):
    iwork_id = models.IntegerField(primary_key=True)
    work = models.OneToOneField('CofkUnionWork', models.DO_NOTHING)
    description = models.TextField(blank=True, null=True)
    date_of_work_std = models.DateField(blank=True, null=True)
    date_of_work_std_year = models.IntegerField(blank=True, null=True)
    date_of_work_std_month = models.IntegerField(blank=True, null=True)
    date_of_work_std_day = models.IntegerField(blank=True, null=True)
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    date_of_work_inferred = models.SmallIntegerField()
    date_of_work_uncertain = models.SmallIntegerField()
    date_of_work_approx = models.SmallIntegerField()
    creators_searchable = models.TextField()
    creators_for_display = models.TextField()
    authors_as_marked = models.TextField(blank=True, null=True)
    notes_on_authors = models.TextField(blank=True, null=True)
    authors_inferred = models.SmallIntegerField()
    authors_uncertain = models.SmallIntegerField()
    addressees_searchable = models.TextField()
    addressees_for_display = models.TextField()
    addressees_as_marked = models.TextField(blank=True, null=True)
    addressees_inferred = models.SmallIntegerField()
    addressees_uncertain = models.SmallIntegerField()
    places_from_searchable = models.TextField()
    places_from_for_display = models.TextField()
    origin_as_marked = models.TextField(blank=True, null=True)
    origin_inferred = models.SmallIntegerField()
    origin_uncertain = models.SmallIntegerField()
    places_to_searchable = models.TextField()
    places_to_for_display = models.TextField()
    destination_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.SmallIntegerField()
    destination_uncertain = models.SmallIntegerField()
    manifestations_searchable = models.TextField()
    manifestations_for_display = models.TextField()
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    people_mentioned = models.TextField(blank=True, null=True)
    images = models.TextField(blank=True, null=True)
    related_resources = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    work_is_translation = models.SmallIntegerField()
    flags = models.TextField(blank=True, null=True)
    edit_status = models.CharField(max_length=3)
    general_notes = models.TextField(blank=True, null=True)
    original_catalogue = models.CharField(max_length=100)
    accession_code = models.CharField(max_length=1000, blank=True, null=True)
    work_to_be_deleted = models.SmallIntegerField()
    change_timestamp = models.DateTimeField(blank=True, null=True)
    change_user = models.CharField(max_length=50)
    drawer = models.CharField(max_length=50, blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    manifestation_type = models.CharField(max_length=50, blank=True, null=True)
    original_notes = models.TextField(blank=True, null=True)
    relevant_to_cofk = models.CharField(max_length=1)
    subjects = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_queryable_work'


class CofkCollectWorkSummary(models.Model):
    upload = models.OneToOneField(CofkCollectWork, models.DO_NOTHING, primary_key=True)
    work_id_in_tool = models.IntegerField()
    source_of_data = models.CharField(max_length=250, blank=True, null=True)
    notes_on_letter = models.TextField(blank=True, null=True)
    date_of_work = models.CharField(max_length=32, blank=True, null=True)
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=30, blank=True, null=True)
    date_of_work_is_range = models.CharField(max_length=30, blank=True, null=True)
    date_of_work_inferred = models.CharField(max_length=30, blank=True, null=True)
    date_of_work_uncertain = models.CharField(max_length=30, blank=True, null=True)
    date_of_work_approx = models.CharField(max_length=30, blank=True, null=True)
    notes_on_date_of_work = models.TextField(blank=True, null=True)
    authors = models.TextField(blank=True, null=True)
    authors_as_marked = models.TextField(blank=True, null=True)
    authors_inferred = models.CharField(max_length=30, blank=True, null=True)
    authors_uncertain = models.CharField(max_length=30, blank=True, null=True)
    notes_on_authors = models.TextField(blank=True, null=True)
    addressees = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    addressees_inferred = models.CharField(max_length=30, blank=True, null=True)
    addressees_uncertain = models.CharField(max_length=30, blank=True, null=True)
    notes_on_addressees = models.TextField(blank=True, null=True)
    destination = models.TextField(blank=True, null=True)
    destination_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.CharField(max_length=30, blank=True, null=True)
    destination_uncertain = models.CharField(max_length=30, blank=True, null=True)
    origin = models.TextField(blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    origin_inferred = models.CharField(max_length=30, blank=True, null=True)
    origin_uncertain = models.CharField(max_length=30, blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    languages_of_work = models.TextField(blank=True, null=True)
    subjects_of_work = models.TextField(blank=True, null=True)
    incipit = models.TextField(blank=True, null=True)
    excipit = models.TextField(blank=True, null=True)
    people_mentioned = models.TextField(blank=True, null=True)
    notes_on_people_mentioned = models.TextField(blank=True, null=True)
    places_mentioned = models.TextField(blank=True, null=True)
    manifestations = models.TextField(blank=True, null=True)
    related_resources = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_work_summary'
        unique_together = (('upload', 'work_id_in_tool'),)
