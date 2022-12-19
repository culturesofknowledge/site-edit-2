from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from core.helper import model_utils
from manifestation.models import CofkUnionManifestation


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


class CofkCollectLocation(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE, null=True)
    location_id = models.IntegerField()
    union_location = models.ForeignKey('CofkUnionLocation', models.DO_NOTHING, blank=True, null=True)

    location_name = models.CharField(max_length=500)
    element_1_eg_room = models.CharField(max_length=100)
    element_2_eg_building = models.CharField(max_length=100)
    element_3_eg_parish = models.CharField(max_length=100)
    element_4_eg_city = models.CharField(max_length=100)
    element_5_eg_county = models.CharField(max_length=100)
    element_6_eg_country = models.CharField(max_length=100)
    element_7_eg_empire = models.CharField(max_length=100)
    notes_on_place = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)  # KTODO what is this _id, should be remove??
    location_synonyms = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_location'
        unique_together = (('upload', 'location_id'),)

    def __str__(self):
        return str(self.union_location)


class CofkCollectLocationResource(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    location_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_location_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkCollectManifestation(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    manifestation_id = models.IntegerField()
    iwork = models.ForeignKey('uploader.models.CofkCollectWork', models.DO_NOTHING)
    union_manifestation = models.ForeignKey(CofkUnionManifestation, models.DO_NOTHING, blank=True, null=True)
    manifestation_type = models.CharField(max_length=3)
    repository = models.ForeignKey('core.models.CofkCollectInstitution', models.DO_NOTHING, blank=True, null=True)
    id_number_or_shelfmark = models.CharField(max_length=500, blank=True, null=True)
    printed_edition_details = models.TextField(blank=True, null=True)
    manifestation_notes = models.TextField(blank=True, null=True)
    image_filenames = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_manifestation'
        unique_together = (('upload', 'iwork_id', 'manifestation_id'),)

    def __str__(self):
        return f'Manifestation #{self.manifestation_id}'


class CofkCollectImageOfManif(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.DO_NOTHING)
    manifestation_id = models.IntegerField()
    image_filename = models.CharField(max_length=2000)
    _id = models.CharField(max_length=32, blank=True, null=True)
    iwork_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_image_of_manif'


class CofkCollectPerson(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    iperson_id = models.IntegerField(blank=True, null=True)
    # KTODO temporary related_name
    union_iperson = models.ForeignKey('CofkUnionPerson', models.DO_NOTHING, blank=True, null=True,
                                      related_name='union_collect_persons')
    person = models.ForeignKey('CofkUnionPerson', models.DO_NOTHING, blank=True, null=True,
                               related_name='collect_persons')
    primary_name = models.CharField(max_length=200)
    alternative_names = models.TextField(blank=True, null=True)
    roles_or_titles = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1)
    is_organisation = models.CharField(max_length=1)
    organisation_type = models.IntegerField(blank=True, null=True)
    date_of_birth_year = models.IntegerField(blank=True, null=True)
    date_of_birth_month = models.IntegerField(blank=True, null=True)
    date_of_birth_day = models.IntegerField(blank=True, null=True)
    date_of_birth_is_range = models.SmallIntegerField()
    date_of_birth2_year = models.IntegerField(blank=True, null=True)
    date_of_birth2_month = models.IntegerField(blank=True, null=True)
    date_of_birth2_day = models.IntegerField(blank=True, null=True)
    date_of_birth_inferred = models.SmallIntegerField()
    date_of_birth_uncertain = models.SmallIntegerField()
    date_of_birth_approx = models.SmallIntegerField()
    date_of_death_year = models.IntegerField(blank=True, null=True)
    date_of_death_month = models.IntegerField(blank=True, null=True)
    date_of_death_day = models.IntegerField(blank=True, null=True)
    date_of_death_is_range = models.SmallIntegerField()
    date_of_death2_year = models.IntegerField(blank=True, null=True)
    date_of_death2_month = models.IntegerField(blank=True, null=True)
    date_of_death2_day = models.IntegerField(blank=True, null=True)
    date_of_death_inferred = models.SmallIntegerField()
    date_of_death_uncertain = models.SmallIntegerField()
    date_of_death_approx = models.SmallIntegerField()
    flourished_year = models.IntegerField(blank=True, null=True)
    flourished_month = models.IntegerField(blank=True, null=True)
    flourished_day = models.IntegerField(blank=True, null=True)
    flourished_is_range = models.SmallIntegerField()
    flourished2_year = models.IntegerField(blank=True, null=True)
    flourished2_month = models.IntegerField(blank=True, null=True)
    flourished2_day = models.IntegerField(blank=True, null=True)
    notes_on_person = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_person'
        unique_together = (('upload', 'iperson_id'),)

    def __str__(self):
        return f'{self.primary_name} (#{self.iperson_id})'


class CofkCollectOccupationOfPerson(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    occupation_of_person_id = models.IntegerField()
    iperson_id = models.IntegerField()
    occupation = models.ForeignKey('core.CofkUnionRoleCategory', models.DO_NOTHING)

    class Meta:
        db_table = 'cofk_collect_occupation_of_person'
        unique_together = (('upload', 'occupation_of_person_id'),)


class CofkCollectPersonResource(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    iperson_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_person_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkCollectWork(models.Model):
    upload = models.ForeignKey(CofkCollectUpload, models.CASCADE)
    iwork_id = models.IntegerField()
    union_iwork = models.ForeignKey('CofkUnionWork', models.DO_NOTHING, blank=True, null=True
                                    , related_name='union_collect_works')
    work = models.ForeignKey('CofkUnionWork', models.DO_NOTHING, blank=True, null=True, related_name='collect_works')
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=2, blank=True, null=True)
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

        if month is not None and not min_month <= month <= max_month:
            self.add_error('%(field)s: is %(value)s but must be between %(min_month)s and %(max_month)s',
                           {'field': field_name, 'value': month, 'min_month': min_month, 'max_month': max_month})

    def clean_date(self, field, field_name, month):
        if field is not None:
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

            try:
                first_date = datetime(self.date_of_work_std_year,
                                      self.date_of_work_std_month, self.date_of_work_std_day)
                second_date = datetime(self.date_of_work2_std_year,
                                       self.date_of_work2_std_month, self.date_of_work2_std_day)
            except TypeError:
                return

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
    iperson = models.ForeignKey('uploader.models.CofkCollectPerson', models.CASCADE)
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
    iperson = models.ForeignKey('uploader.models.CofkCollectPerson', models.CASCADE)
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
    location = models.ForeignKey('uploader.models.CofkCollectLocation', models.CASCADE)
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
    language_code = models.ForeignKey('core.Iso639LanguageCode', models.DO_NOTHING, db_column='language_code')
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.language_code)

    class Meta:
        db_table = 'cofk_collect_language_of_work'
        unique_together = (('upload', 'iwork_id', 'language_of_work_id'),)


class CofkCollectOriginOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    origin_id = models.IntegerField()
    location = models.ForeignKey('uploader.models.CofkCollectLocation', models.CASCADE)
    iwork = models.ForeignKey('work.CofkCollectWork', models.CASCADE)
    notes_on_origin = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.location)

    class Meta:
        db_table = 'cofk_collect_origin_of_work'
        unique_together = (('upload', 'iwork', 'origin_id'),)


class CofkCollectPersonMentionedInWork(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", null=False, on_delete=models.CASCADE)
    mention_id = models.IntegerField()
    iperson = models.ForeignKey('uploader.models.CofkCollectPerson', models.CASCADE)
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
    subject = models.ForeignKey('core.CofkUnionSubject', models.DO_NOTHING)

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


class CofkCollectInstitution(models.Model):
    upload = models.ForeignKey("uploader.CofkCollectUpload", on_delete=models.CASCADE)
    institution_id = models.IntegerField()
    # TODO under what circumstances is this populated? it is clearly not populated when spreadsheet is uploaded
    union_institution = models.ForeignKey('CofkUnionInstitution', models.DO_NOTHING, blank=True, null=True)
    institution_name = models.TextField()
    institution_city = models.TextField()
    institution_country = models.TextField()
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)
    institution_synonyms = models.TextField(blank=True, null=True)
    institution_city_synonyms = models.TextField(blank=True, null=True)
    institution_country_synonyms = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_institution'
        unique_together = (('upload', 'institution_id'),)

    def __str__(self):
        return f'{self.institution_name} (#{self.institution_id})'


class CofkCollectInstitutionResource(models.Model):
    upload = models.OneToOneField('uploader.CofkCollectUpload', models.DO_NOTHING)
    resource_id = models.IntegerField()
    institution_id = models.IntegerField()
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_institution_resource'
        unique_together = (('upload', 'resource_id'),)
