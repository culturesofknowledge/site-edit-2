import uuid as uuid
from django.db import models


class CofkUnionWork(models.Model):
    work_id = models.CharField(max_length=100)
    description = models.TextField(null=True)
    date_of_work_as_marked = models.CharField(max_length=250)
    original_calendar = models.CharField(max_length=2, null=False, default='')
    date_of_work_std = models.CharField(max_length=12)
    date_of_work_std_gregorian = models.CharField(max_length=12)
    date_of_work_std_year = models.IntegerField(null=True)
    date_of_work_std_month = models.IntegerField(null=True)
    date_of_work_std_day = models.IntegerField(null=True)
    date_of_work2_std_year = models.IntegerField(null=True)
    date_of_work2_std_month = models.IntegerField(null=True)
    date_of_work2_std_day = models.IntegerField(null=True)
    date_of_work_std_is_range = models.BooleanField(null=False, default=False)
    date_of_work_inferred = models.BooleanField(null=False, default=False)
    date_of_work_uncertain = models.BooleanField(null=False, default=False)
    date_of_work_approx = models.BooleanField(null=False, default=False)
    authors_as_marked = models.TextField(null=True)
    addressees_as_marked = models.TextField(null=True)
    authors_inferred = models.BooleanField(null=False, default=False)
    authors_uncertain = models.BooleanField(null=False, default=False)
    addressees_inferred = models.BooleanField(null=False, default=False)
    addressees_uncertain = models.BooleanField(null=False, default=False)
    destination_as_marked = models.TextField(null=True)
    origin_as_marked = models.TextField(null=True)
    destination_inferred = models.BooleanField(null=False, default=False)
    destination_uncertain = models.BooleanField(null=False, default=False)
    origin_inferred = models.BooleanField(null=False, default=False)
    origin_uncertain = models.BooleanField(null=False, default=False)
    abstract = models.TextField(null=True)
    keywords = models.TextField(null=True)
    language_of_work = models.CharField(max_length=255)
    work_is_translation = models.BooleanField(null=False, default=False)
    incipit = models.TextField(null=True)
    explicit = models.TextField(null=True)
    ps = models.TextField(null=True)
    original_catalogue = models.ForeignKey("uploader.CofkLookupCatalogue", null=False, default='',
                                           on_delete=models.DO_NOTHING)
    accession_code = models.CharField(max_length=1000)
    work_to_be_deleted = models.BooleanField(null=False, default=False)
    iwork_id = models.AutoField(primary_key=True, null=False, unique=True)
    editors_notes = models.TextField(null=True)
    edit_status = models.CharField(max_length=3, null=False, default='')
    relevant_to_cofk = models.CharField(max_length=3, null=False, default='Y')
    creation_timestamp = models.DateTimeField(auto_now=True)
    change_timestamp = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4)


class CofkCollectWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    iwork_id = models.AutoField(primary_key=True)
    union_iwork_id = models.ForeignKey("CofkUnionWork", null=True, on_delete=models.DO_NOTHING)
    date_of_work_as_marked = models.CharField(max_length=250)
    original_calendar = models.CharField(max_length=2, null=False, default='')
    date_of_work_std_year = models.IntegerField(null=True)
    date_of_work_std_month = models.IntegerField(null=True)
    date_of_work_std_day = models.IntegerField(null=True)
    date_of_work2_std_year = models.IntegerField(null=True)
    date_of_work2_std_month = models.IntegerField(null=True)
    date_of_work2_std_day = models.IntegerField(null=True)
    date_of_work_std_is_range = models.BooleanField(null=True, default=False)
    date_of_work_inferred = models.BooleanField(null=True, default=False)
    date_of_work_uncertain = models.BooleanField(null=True, default=False)
    date_of_work_approx = models.BooleanField(null=True, default=False)
    notes_on_date_of_work = models.TextField(null=True)
    authors_as_marked = models.TextField(null=True)
    authors_inferred = models.BooleanField(null=True, default=False)
    authors_uncertain = models.BooleanField(null=True, default=False)
    notes_on_authors = models.TextField(null=True)
    addressees_as_marked = models.TextField(null=True)
    addressees_inferred = models.BooleanField(null=True, default=False)
    addressees_uncertain = models.BooleanField(null=True, default=False)
    notes_on_addressees = models.TextField(null=True)
    destination_id = models.IntegerField(null=True)
    destination_as_marked = models.TextField(null=True)
    destination_inferred = models.BooleanField(null=True, default=False)
    destination_uncertain = models.BooleanField(null=True, default=False)
    origin_id = models.IntegerField(null=True)
    origin_as_marked = models.TextField(null=True)
    origin_inferred = models.BooleanField(null=True, default=False)
    origin_uncertain = models.BooleanField(null=True, default=False)
    abstract = models.TextField(null=True)
    keywords = models.TextField(null=True)
    language_of_work = models.CharField(max_length=255)
    incipit = models.TextField(null=True)
    excipit = models.TextField(null=True)
    accession_code = models.CharField(max_length=250)
    notes_on_letter = models.TextField(null=True)
    notes_on_people_mentioned = models.TextField(null=True)
    upload_status = models.ForeignKey("uploader.CofkCollectStatus", null=False, default="1",
                                      on_delete=models.DO_NOTHING)
    editors_notes = models.TextField(null=True)
    _id = models.CharField(max_length=32)
    date_of_work2_approx = models.BooleanField(null=True, default=False)
    date_of_work2_inferred = models.BooleanField(null=True, default=False)
    date_of_work2_uncertain = models.BooleanField(null=True, default=False)
    mentioned_as_marked = models.TextField(null=True)
    mentioned_inferred = models.BooleanField(null=True, default=False)
    mentioned_uncertain = models.BooleanField(null=True, default=False)
    notes_on_destination = models.TextField(null=True)
    notes_on_origin = models.TextField(null=True)
    notes_on_place_mentioned = models.TextField(null=True)
    place_mentioned_as_marked = models.TextField(null=True)
    place_mentioned_inferred = models.BooleanField(null=True, default=False)
    place_mentioned_uncertain = models.BooleanField(null=True, default=False)
    upload_name = models.CharField(max_length=254)
    explicit = models.TextField(null=True)


class CofkCollectAddresseeOfWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", on_delete=models.CASCADE)
    addressee_id = models.AutoField(primary_key=True)
    iperson_id = models.IntegerField(null=False)
    notes_on_addressee = models.TextField(null=True)
    _id = models.CharField(max_length=32)


class CofkCollectAuthorOfWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    author_id = models.AutoField(primary_key=True)
    iperson_id = models.IntegerField(null=False)
    notes_on_author = models.TextField(null=True)
    _id = models.CharField(max_length=32)


class CofkCollectDestinationOfWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", on_delete=models.CASCADE)
    destination_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    notes_on_destination = models.TextField(null=True)
    _id = models.CharField(max_length=32)


class CofkCollectLanguageOfWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    language_of_work_id = models.AutoField(primary_key=True)
    language_code = models.ForeignKey("uploader.Iso639LanguageCode", null=False, on_delete=models.DO_NOTHING)
    _id = models.CharField(max_length=32)


class CofkCollectOriginOfWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", on_delete=models.CASCADE)
    origin_id = models.AutoField(primary_key=True)
    location_id = models.IntegerField(null=False)
    notes_on_origin = models.TextField(null=True)
    _id = models.CharField(max_length=32)


class CofkCollectPersonMentionedInWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    iperson_id = models.IntegerField(null=False)
    notes_on_person_mentioned = models.TextField(null=True)
    _id = models.CharField(max_length=32)


class CofkCollectPlaceMentionedInWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    location_id = models.IntegerField(null=False)
    notes_on_place_mentioned = models.TextField(null=True)
    _id = models.CharField(max_length=32)


class CofkCollectSubjectOfWork(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    subject_of_work_id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey("uploader.CofkUnionSubject", on_delete=models.CASCADE, null=False)


class CofkCollectWorkResource(models.Model):
    upload_id = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    resource_name = models.TextField(null=False, default='')
    resource_details = models.TextField(null=False, default='')
    resource_url = models.TextField(null=False, default='')
    _id = models.CharField(max_length=32)


class CofkUnionLanguageOfWork(models.Model):
    work_id = models.OneToOneField("CofkUnionWork", on_delete=models.CASCADE, null=False)
    language_code = models.ForeignKey("uploader.Iso639LanguageCode", on_delete=models.CASCADE, null=False)
    notes = models.CharField(max_length=100)
