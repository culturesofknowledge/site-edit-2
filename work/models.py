import functools
from datetime import datetime
from typing import Iterable

from django.core.exceptions import ValidationError
from django.db import models

from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_COMMENT_DATE, \
    REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO
from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref
from uploader.models import CofkCollectUpload, CofkCollectStatus

SEQ_NAME_COFKUNIONWORK__IWORK_ID = 'cofk_union_person_iwork_id_seq'


class CofkUnionWork(models.Model, RecordTracker):
    work_id = models.CharField(primary_key=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=2, default='')
    date_of_work_std = models.CharField(max_length=12, blank=True, null=True, default='9999-12-31')
    date_of_work_std_gregorian = models.CharField(max_length=12, blank=True, null=True, default='9999-12-31')
    date_of_work_std_year = models.IntegerField(blank=True, null=True)
    date_of_work_std_month = models.IntegerField(blank=True, null=True)
    date_of_work_std_day = models.IntegerField(blank=True, null=True)
    date_of_work2_std_year = models.IntegerField(blank=True, null=True)
    date_of_work2_std_month = models.IntegerField(blank=True, null=True)
    date_of_work2_std_day = models.IntegerField(blank=True, null=True)
    date_of_work_std_is_range = models.SmallIntegerField(default=0)
    date_of_work_inferred = models.SmallIntegerField(default=0)
    date_of_work_uncertain = models.SmallIntegerField(default=0)
    date_of_work_approx = models.SmallIntegerField(default=0)
    authors_as_marked = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    authors_inferred = models.SmallIntegerField(default=0)
    authors_uncertain = models.SmallIntegerField(default=0)
    addressees_inferred = models.SmallIntegerField(default=0)
    addressees_uncertain = models.SmallIntegerField(default=0)
    destination_as_marked = models.TextField(blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.SmallIntegerField(default=0)
    destination_uncertain = models.SmallIntegerField(default=0)
    origin_inferred = models.SmallIntegerField(default=0)
    origin_uncertain = models.SmallIntegerField(default=0)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    work_is_translation = models.SmallIntegerField(default=0)
    incipit = models.TextField(blank=True, null=True)
    explicit = models.TextField(blank=True, null=True)
    ps = models.TextField(blank=True, null=True)
    original_catalogue = models.ForeignKey("uploader.CofkLookupCatalogue", models.DO_NOTHING,
                                           db_column='original_catalogue', blank=True, null=True,
                                           default='')
    accession_code = models.CharField(max_length=1000, blank=True, null=True)
    work_to_be_deleted = models.SmallIntegerField(default=0)
    iwork_id = models.IntegerField(
        default=functools.partial(model_utils.next_seq_safe, SEQ_NAME_COFKUNIONWORK__IWORK_ID),
        unique=True,
    )
    editors_notes = models.TextField(blank=True, null=True)
    edit_status = models.CharField(max_length=3, default='')
    relevant_to_cofk = models.CharField(max_length=3, default='Y')
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True, default=model_utils.default_uuid)

    class Meta:
        db_table = 'cofk_union_work'

    def find_comments_by_rel_type(self, rel_type) -> Iterable['CofkUnionComment']:
        return (r.comment for r in self.cofkworkcomment_set.filter(relationship_type=rel_type))

    @property
    def author_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(REL_TYPE_COMMENT_AUTHOR)

    @property
    def addressee_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(REL_TYPE_COMMENT_ADDRESSEE)

    @property
    def date_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(REL_TYPE_COMMENT_DATE)

    def find_location_by_rel_type(self, rel_type) -> 'CofkWorkLocationMap':
        return self.cofkworklocationmap_set.filter(relationship_type=rel_type).first()

    @property
    def origin_location(self) -> 'CofkWorkLocationMap':
        return self.find_location_by_rel_type(REL_TYPE_WAS_SENT_FROM)

    @property
    def destination_location(self) -> 'CofkWorkLocationMap':
        return self.find_location_by_rel_type(REL_TYPE_WAS_SENT_TO)


class CofkWorkCommentMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_comment_map'


class CofkWorkWorkMap(Recref):
    work_from = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE,
                                  related_name='work_from_set', )
    work_to = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE,
                                related_name='work_to_set', )

    class Meta(Recref.Meta):
        db_table = 'cofk_work_work_map'


class CofkWorkPersonMap(Recref):
    """
    possible relationship_type [signed, created, sent]
    """
    work = models.ForeignKey(CofkUnionWork,
                             on_delete=models.CASCADE)
    person = models.ForeignKey("person.CofkUnionPerson",
                               on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_person_map'


class CofkWorkLocationMap(Recref):
    work = models.ForeignKey(CofkUnionWork,
                             on_delete=models.CASCADE)
    location = models.ForeignKey("location.CofkUnionLocation",
                                 on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_location_map'


class CofkCollectWork(models.Model):
    upload = models.ForeignKey(CofkCollectUpload, models.CASCADE)
    iwork_id = models.IntegerField()
    union_iwork = models.ForeignKey('CofkUnionWork', models.DO_NOTHING, blank=True, null=True
                                    , related_name='union_collect_works')
    work = models.ForeignKey('CofkUnionWork', models.DO_NOTHING, blank=True, null=True, related_name='collect_works')
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=2)
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
    notes_on_date_of_work = models.TextField(blank=True, null=True)
    authors_as_marked = models.TextField(blank=True, null=True)
    authors_inferred = models.SmallIntegerField()
    authors_uncertain = models.SmallIntegerField()
    notes_on_authors = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    addressees_inferred = models.SmallIntegerField()
    addressees_uncertain = models.SmallIntegerField()
    notes_on_addressees = models.TextField(blank=True, null=True)
    # destination_id = models.IntegerField(blank=True, null=True)
    destination = models.ForeignKey('CofkCollectDestinationOfWork', models.CASCADE, blank=True, null=True)
    destination_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.SmallIntegerField()
    destination_uncertain = models.SmallIntegerField()
    # origin_id = models.IntegerField(blank=True, null=True)
    origin = models.ForeignKey('CofkCollectOriginOfWork', models.CASCADE, blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    origin_inferred = models.SmallIntegerField()
    origin_uncertain = models.SmallIntegerField()
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    incipit = models.TextField(blank=True, null=True)
    excipit = models.TextField(blank=True, null=True)
    accession_code = models.CharField(max_length=250, blank=True, null=True)
    notes_on_letter = models.TextField(blank=True, null=True)
    notes_on_people_mentioned = models.TextField(blank=True, null=True)
    upload_status = models.ForeignKey(CofkCollectStatus, models.DO_NOTHING, db_column='upload_status')
    editors_notes = models.TextField(blank=True, null=True)
    _id = models.CharField(db_column='_id', max_length=32, blank=True,
                           null=True)  # Field renamed because it started with '_'.
    date_of_work2_approx = models.SmallIntegerField()
    date_of_work2_inferred = models.SmallIntegerField()
    date_of_work2_uncertain = models.SmallIntegerField()
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

    errors = []

    class Meta:
        db_table = 'cofk_collect_work'
        unique_together = (('upload', 'iwork_id'),)

    def __str__(self):
        return f'Work #{self.iwork_id}'

    def clean_year(self, year, field_name):
        max_year = 1900
        min_year = 1500

        if not max_year >= year >= min_year:
            self.add_error('%(field)s: is %(value)s but must be between %(min_year)s and %(max_year)s',
                           {'field': field_name, 'value': year, 'min_year': min_year, 'max_year': max_year})

    def clean_month(self, month, field_name):
        min_month = 1
        max_month = 12

        if not min_month <= month <= max_month:
            self.add_error('%(field)s: is %(value)s but must be between %(min_month)s and %(max_month)s',
                           {'field': field_name, 'value': month, 'min_month': min_month, 'max_month': max_month})

    def clean_date(self, field, field_name, month):
        if field < 1:
            self.add_error('%(field)s: can not be less than 1', {'field': field_name})
        elif field > 31:
            self.add_error('%(field)s: can not be greater than 31', {'field': field_name})
        # If month is April, June, September or November then day must be not more than 30
        elif month in [4, 6, 9, 11] and field > 30:
            self.add_error('%(field)s: can not be more than 30 for April, June, September or November',
                           {'field': field_name})
        # For February not more than 29
        elif month == 2 and field > 29:
            self.add_error('%(field)s: can not be more than 29 for February', {'field': field_name})

    def clean_range(self):
        if self.date_of_work_std_is_range == 1:
            if self.date_of_work2_std_year is None:
                self.add_error('%(field)s: can not be empty when %(field2)s is 1',
                               {'field': 'date_of_work2_std_year', 'field2': 'date_of_work_std_is_range'})

            self.clean_date(self.date_of_work2_std_day, 'date_of_work2_std_day', self.date_of_work2_std_month)

            first_date = datetime(self.date_of_work_std_year,
                                  self.date_of_work_std_month, self.date_of_work_std_day)
            second_date = datetime(self.date_of_work2_std_year,
                                   self.date_of_work2_std_month, self.date_of_work2_std_day)
            if first_date >= second_date:
                self.add_error('%(field1)s-%(field2)s: The start date in a date range can not be after the end date',
                               {'field1': 'date_of_work', 'field2': 'date_of_work2'})

    def clean_date_notes(self):
        if self.notes_on_date_of_work is not None and self.notes_on_date_of_work[0].islower():
            self.add_error('%(field)s: Notes with dates have to start with an upper case letter',
                           {'field': 'notes_on_date_of_work'})

        if self.notes_on_date_of_work is not None and self.notes_on_date_of_work[-1] != '.':
            self.add_error('%(field)s: Notes with dates have to end with a full stop',
                           {'field': 'notes_on_date_of_work'})

    def clean(self):
        # Reset error count
        self.errors = []
        # Clean year values
        self.clean_year(self.date_of_work_std_year, 'date_of_work_std_year')

        if self.date_of_work2_std_year:
            self.clean_year(self.date_of_work2_std_year, 'date_of_work2_std_year')

        # Clean month values
        self.clean_month(self.date_of_work_std_month, 'date_of_work_std_month')

        if self.date_of_work2_std_month:
            self.clean_month(self.date_of_work2_std_month, 'date_of_work2_std_month')

        # Clean date values
        if self.date_of_work_std_day:
            self.clean_date(self.date_of_work_std_day, 'date_of_work_std_day', self.date_of_work_std_month)

        # Clean date range
        self.clean_range()

        # Clean notes on date
        self.clean_date_notes()

        # Clean locations

        if self.errors:
            raise ValidationError(self.errors)

    def add_error(self, msg, params):
        self.errors.append(ValidationError(msg, params=params))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def date_of_work_std(self):
        try:
            return datetime(self.date_of_work_std_year, self.date_of_work_std_month, self.date_of_work_std_day) \
                .strftime("%d %b %Y")
        except Exception:
            pass

    @property
    def date_of_work2_std(self):
        try:
            return datetime(self.date_of_work2_std_year, self.date_of_work2_std_month, self.date_of_work2_std_day) \
                .strftime("%d %b %Y")
        except Exception:
            pass

    @property
    def display_daterange(self):
        if self.date_of_work_std and self.date_of_work2_std:
            return f'{self.date_of_work_std} to {self.date_of_work2_std}'
        elif self.date_of_work_std:
            return f'{self.date_of_work_std} to ????-??-??'

        return f'????-??-?? To {self.date_of_work2_std}'

    @property
    def display_original_calendar(self):
        if self.original_calendar == 'G':
            return 'Gregorian'
        elif self.original_calendar == 'J':
            return 'Julian'  # This will switch to "JJ" after accepted, see review.php
        elif self.original_calendar == 'JJ':
            return 'Julian (January year start)'
        elif self.original_calendar == 'JM':
            return 'Julian (March year start)'

    @property
    def display_date_issues(self):
        issues = []

        if self.date_of_work_std_is_range == 1:
            issues.append('estimated or known range')

        if self.date_of_work_inferred == 1:
            issues.append('inferred')

        if self.date_of_work_uncertain == 1:
            issues.append('uncertain')

        if self.date_of_work_approx == 1:
            issues.append('approximate')

        return ', '.join(issues)

    @property
    def display_origin_issues(self):
        issues = []

        if self.origin_inferred == 1:
            issues.append('inferred')

        if self.origin_uncertain == 1:
            issues.append('uncertain')

        return ', '.join(issues)

    @property
    def display_destination_issues(self):
        issues = []

        if self.destination_inferred == 1:
            issues.append('inferred')

        if self.destination_uncertain == 1:
            issues.append('uncertain')

        return ', '.join(issues)

    @property
    def display_authors_issues(self):
        issues = []

        if self.authors_inferred == 1:
            issues.append('inferred')

        if self.authors_uncertain == 1:
            issues.append('uncertain')

        return ', '.join(issues)

    @property
    def display_addressees_issues(self):
        issues = []

        if self.addressees_inferred == 1:
            issues.append('inferred')

        if self.addressees_uncertain == 1:
            issues.append('uncertain')

        return ', '.join(issues)

    @property
    def display_mentioned_issues(self):
        issues = []

        if self.mentioned_inferred == 1:
            issues.append('inferred')

        if self.mentioned_uncertain == 1:
            issues.append('uncertain')

        return ', '.join(issues)


class CofkCollectAddresseeOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    addressee_id = models.IntegerField()
    iperson = models.ForeignKey('person.CofkCollectPerson', models.CASCADE)
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    notes_on_addressee = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.iperson)

    class Meta:
        db_table = 'cofk_collect_addressee_of_work'
        unique_together = (('upload', 'iwork_id', 'addressee_id'),)


class CofkCollectAuthorOfWork(models.Model):
    """
    This table is required only for collect purposes, as best I understand, and is not used
    in other regards. Only exception is Tweaker, see:
    https://github.com/culturesofknowledge/site-edit/blob/9a74580d2567755ab068a2d8761df8f81718910e/emlo-edit-php-helper/tweaker/tweaker/uploader.py#L739-L770
    This table, like other ***OfWork tables is used as a link between CofkCollectWork and the
    respective main entity table. This table links CofkCollectWork with CofkCollectPerson using
    iperson_id as a unique key in CofkCollectPerson and iwork_id as a unique key in CofkCollectWork.
    Author_id is then the unique key in this table, however, in the original schema the primary key
    is set as a composite key of the three, upload_id, iwork_id and author_id and iperson_id is set
    as a composite key of upload_id and iperson_id in CofkCollectPerson.
    However, as Django does not support composite keys in database models, a workaround is to
    designate iperson_id and iwork_id as many-to-many-relationship fields.
    """
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    author_id = models.IntegerField()
    iperson = models.ForeignKey('person.CofkCollectPerson', models.CASCADE)
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    notes_on_author = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.iperson)

    class Meta:
        db_table = 'cofk_collect_author_of_work'
        unique_together = (('upload', 'iwork_id', 'author_id'),)


class CofkCollectDestinationOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    destination_id = models.IntegerField()
    location = models.ForeignKey('location.CofkCollectLocation', models.CASCADE)
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    notes_on_destination = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.location)

    class Meta:
        db_table = 'cofk_collect_destination_of_work'
        unique_together = (('upload', 'iwork_id', 'destination_id'),)


class CofkCollectLanguageOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    language_of_work_id = models.IntegerField()
    iwork = models.ForeignKey('work.CofkCollectWork', models.DO_NOTHING)
    language_code = models.ForeignKey('uploader.Iso639LanguageCode', models.DO_NOTHING, db_column='language_code')
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.language_code)

    class Meta:
        db_table = 'cofk_collect_language_of_work'
        unique_together = (('upload', 'iwork_id', 'language_of_work_id'),)


class CofkCollectOriginOfWork(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.CASCADE)
    origin_id = models.IntegerField()
    location = models.ForeignKey('location.CofkCollectLocation', models.CASCADE)
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    notes_on_origin = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.location)

    class Meta:
        db_table = 'cofk_collect_origin_of_work'
        unique_together = (('upload', 'iwork_id', 'origin_id'),)


class CofkCollectPersonMentionedInWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    mention_id = models.IntegerField()
    iperson = models.ForeignKey('person.CofkCollectPerson', models.CASCADE)
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    notes_on_person_mentioned = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32)

    def __str__(self):
        return str(self.iperson)

    class Meta:
        db_table = 'cofk_collect_person_mentioned_in_work'
        unique_together = (('upload', 'iwork_id', 'mention_id'),)


class CofkCollectPlaceMentionedInWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    mention_id = models.IntegerField()
    location_id = models.IntegerField()
    iwork_id = models.IntegerField()
    notes_on_place_mentioned = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_place_mentioned_in_work'
        unique_together = (('upload', 'iwork_id', 'mention_id'),)


class CofkCollectSubjectOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    subject_of_work_id = models.IntegerField()
    iwork_id = models.IntegerField()
    subject = models.ForeignKey('uploader.CofkUnionSubject', models.DO_NOTHING)

    class Meta:
        db_table = 'cofk_collect_subject_of_work'
        unique_together = (('upload', 'iwork_id', 'subject_of_work_id'),)


class CofkCollectWorkResource(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    resource_id = models.IntegerField()
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_work_resource'
        unique_together = (('upload', 'iwork_id', 'resource_id'),)


class CofkUnionLanguageOfWork(models.Model):
    work = models.OneToOneField('CofkUnionWork', models.DO_NOTHING, primary_key=True)
    language_code = models.ForeignKey('uploader.Iso639LanguageCode', models.DO_NOTHING, db_column='language_code')
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
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
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


def create_work_id(iwork_id) -> str:
    return f'cofk_union_work-iwork_id:{iwork_id}'
