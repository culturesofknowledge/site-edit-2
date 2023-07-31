from datetime import datetime

from django.db import models

from manifestation.manif_utils import get_doctype_desc


class CofkCollectStatus(models.Model):
    '''
    1    Awaiting review
    2    Partly reviewed
    3    Review complete
    4    Accepted and saved into main database
    5    Rejected
    ''' 
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


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.upload_username, filename)


class CofkCollectUpload(models.Model):
    upload_id = models.AutoField(primary_key=True)
    upload_username = models.CharField(max_length=100)
    upload_description = models.TextField(blank=True, null=True)
    upload_status = models.ForeignKey(CofkCollectStatus, models.SET_NULL, db_column='upload_status',
                                      null=True)
    upload_timestamp = models.DateTimeField()
    total_works = models.IntegerField(default=0)
    works_accepted = models.IntegerField(default=0)
    works_rejected = models.IntegerField(default=0)
    uploader_email = models.CharField(max_length=250, default='')
    _id = models.CharField(max_length=32, blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    upload_file = models.FileField(upload_to=user_directory_path)  # TODO schema changed for current system

    class Meta:
        db_table = 'cofk_collect_upload'


class CofkCollectToolSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    session_timestamp = models.DateTimeField()
    session_code = models.TextField(unique=True, blank=True, null=True)
    username = models.ForeignKey(CofkCollectToolUser, models.SET_NULL, db_column='username', blank=True,
                                 null=True)

    class Meta:
        db_table = 'cofk_collect_tool_session'


class CofkCollectLocation(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    location_id = models.IntegerField()
    union_location = models.ForeignKey('location.CofkUnionLocation', models.SET_NULL, blank=True, null=True)
    location_name = models.CharField(max_length=500, default='')
    element_1_eg_room = models.CharField(max_length=100, default='')
    element_2_eg_building = models.CharField(max_length=100, default='')
    element_3_eg_parish = models.CharField(max_length=100, default='')
    element_4_eg_city = models.CharField(max_length=100, default='')
    element_5_eg_county = models.CharField(max_length=100, default='')
    element_6_eg_country = models.CharField(max_length=100, default='')
    element_7_eg_empire = models.CharField(max_length=100, default='')
    notes_on_place = models.TextField(blank=True, null=True)
    editors_notes = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)
    location_synonyms = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_location'
        unique_together = (('upload', 'location_id'),)

    def to_string(self):
        location = self.location_name
        if self.union_location_id:
            location += f' [ID {self.union_location_id}]'

        if self.editors_notes:
            location += f' [editor\'s notes: {self.editors_notes}]'

        return location

    def __str__(self):
        return str(self.union_location) if self.union_location is not None else f'{self.location_name} (collect)'


class CofkCollectLocationResource(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    resource_id = models.IntegerField()
    location = models.ForeignKey('uploader.CofkCollectLocation', models.CASCADE)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_location_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkCollectManifestation(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    manifestation_id = models.IntegerField()
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='manifestations')
    union_manifestation = models.ForeignKey('manifestation.CofkUnionManifestation',
                                            models.SET_NULL, blank=True, null=True)
    manifestation_type = models.CharField(max_length=3)
    repository = models.ForeignKey('uploader.CofkCollectInstitution', models.CASCADE, blank=True, null=True)
    id_number_or_shelfmark = models.CharField(max_length=500, blank=True, null=True)
    printed_edition_details = models.TextField(blank=True, null=True)
    manifestation_notes = models.TextField(blank=True, null=True)
    image_filenames = models.TextField(blank=True, null=True)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_manifestation'
        unique_together = (('upload', 'iwork_id', 'manifestation_id'),)

    def to_string(self):
        manif = get_doctype_desc(self) + '. '

        if self.repository:
            manif += f'Repository: {self.repository.institution_name}. '

        if self.id_number_or_shelfmark:
            manif += f'Shelfmark: {self.id_number_or_shelfmark}. '

        if self.printed_edition_details:
            manif += f'Printed edition details: {self.printed_edition_details}. '

        if self.manifestation_notes:
            manif += f'Notes on document: {self.manifestation_notes}. '

        return manif


class CofkCollectImageOfManif(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    manifestation_id = models.IntegerField()
    image_filename = models.CharField(max_length=2000)
    _id = models.CharField(max_length=32, blank=True, null=True)
    iwork_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_image_of_manif'


class CofkCollectPerson(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    iperson_id = models.IntegerField()
    union_iperson = models.ForeignKey('person.CofkUnionPerson', models.SET_NULL, blank=True, null=True,
                                      to_field='iperson_id', related_name='union_collect_persons')
    person_id = models.CharField(max_length=100, null=True)
    primary_name = models.CharField(max_length=200)
    alternative_names = models.TextField(blank=True, null=True)
    roles_or_titles = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1)
    is_organisation = models.CharField(max_length=1)
    organisation_type = models.IntegerField(blank=True, null=True)
    date_of_birth_year = models.IntegerField(blank=True, null=True)
    date_of_birth_month = models.IntegerField(blank=True, null=True)
    date_of_birth_day = models.IntegerField(blank=True, null=True)
    date_of_birth_is_range = models.SmallIntegerField(default=0)
    date_of_birth2_year = models.IntegerField(blank=True, null=True)
    date_of_birth2_month = models.IntegerField(blank=True, null=True)
    date_of_birth2_day = models.IntegerField(blank=True, null=True)
    date_of_birth_inferred = models.SmallIntegerField(default=0)
    date_of_birth_uncertain = models.SmallIntegerField(default=0)
    date_of_birth_approx = models.SmallIntegerField(default=0)
    date_of_death_year = models.IntegerField(blank=True, null=True)
    date_of_death_month = models.IntegerField(blank=True, null=True)
    date_of_death_day = models.IntegerField(blank=True, null=True)
    date_of_death_is_range = models.SmallIntegerField(default=0)
    date_of_death2_year = models.IntegerField(blank=True, null=True)
    date_of_death2_month = models.IntegerField(blank=True, null=True)
    date_of_death2_day = models.IntegerField(blank=True, null=True)
    date_of_death_inferred = models.SmallIntegerField(default=0)
    date_of_death_uncertain = models.SmallIntegerField(default=0)
    date_of_death_approx = models.SmallIntegerField(default=0)
    flourished_year = models.IntegerField(blank=True, null=True)
    flourished_month = models.IntegerField(blank=True, null=True)
    flourished_day = models.IntegerField(blank=True, null=True)
    flourished_is_range = models.SmallIntegerField(default=0)
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

    def to_string(self, is_details=False) -> str:
        """
        Used by work.creators_for_display and work.addressees_for_display
        """
        dob = str(self.date_of_birth_year)
        dod = str(self.date_of_death_year)

        if self.date_of_death_is_range == 1:
            dod += ' or after'

        if self.date_of_birth_is_range == 1:
            dob += ' or before'

        if self.date_of_birth_year and self.date_of_death_year:
            person = f'{self.primary_name}, {dob}-{dod}'
        elif self.date_of_birth_year:
            person = f'{self.primary_name} b. {dob}'
        elif self.date_of_death_year:
            person = f'{self.primary_name} d. {dod}'
        else:
            person = str(self.primary_name)

        fos = str(self.flourished_year)
        foe = str(self.flourished2_year)

        if self.flourished_year and self.flourished2_year:
            person += f', fl. {fos}-{foe}'
        elif self.flourished_year:
            person += f', fl. {fos}'

        return person

    #def __str__(self):
    #    return str(self.union_iperson) if self.union_iperson is not None else f'{self.primary_name} (collect)'


class CofkCollectOccupationOfPerson(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    occupation_of_person_id = models.IntegerField()
    iperson = models.ForeignKey('uploader.CofkCollectPerson', models.CASCADE)
    occupation = models.ForeignKey('core.CofkUnionRoleCategory', models.CASCADE)

    class Meta:
        db_table = 'cofk_collect_occupation_of_person'
        unique_together = (('upload', 'occupation_of_person_id'),)


class CofkCollectPersonResource(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    resource_id = models.IntegerField()
    iperson = models.ForeignKey('uploader.CofkCollectPerson', models.CASCADE)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_person_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkCollectWorkSummary(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    work_id_in_tool = models.OneToOneField('uploader.CofkCollectWork', models.CASCADE)
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
    union_institution = models.ForeignKey('institution.CofkUnionInstitution', models.SET_NULL, blank=True, null=True)
    institution_name = models.TextField(default='')
    institution_city = models.TextField(default='')
    institution_country = models.TextField(default='')
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)
    institution_synonyms = models.TextField(blank=True, null=True)
    institution_city_synonyms = models.TextField(blank=True, null=True)
    institution_country_synonyms = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_institution'
        unique_together = (('upload', 'institution_id'),)

    def __str__(self):
        return str(self.union_institution) if \
            self.union_institution is not None else f'{self.institution_name} (collect)'


class CofkCollectInstitutionResource(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    resource_id = models.IntegerField()
    institution = models.ForeignKey('uploader.CofkCollectInstitution', models.CASCADE)
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()

    class Meta:
        db_table = 'cofk_collect_institution_resource'
        unique_together = (('upload', 'resource_id'),)


class CofkCollectWork(models.Model):
    '''
    The columns destination_id and origin_id are redundant as, even though they link to CofkCollectOriginOfWork and
     CofkCollectDestinationOfWork, Django ORM already provides a link to them via related name.
    '''
    upload = models.ForeignKey('CofkCollectUpload', models.CASCADE, related_name='upload')
    iwork_id = models.IntegerField()
    union_iwork = models.ForeignKey('work.CofkUnionWork', models.SET_NULL, blank=True, null=True,
                                    to_field='iwork_id', related_name='union_collect_works')
    work = models.ForeignKey('work.CofkUnionWork', models.SET_NULL, blank=True, null=True,
                             related_name='collect_works')
    date_of_work_as_marked = models.CharField(max_length=250, blank=True, null=True)
    original_calendar = models.CharField(max_length=2, blank=True, null=True)
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
    notes_on_date_of_work = models.TextField(blank=True, null=True)
    authors_as_marked = models.TextField(blank=True, null=True)
    authors_inferred = models.SmallIntegerField(default=0)
    authors_uncertain = models.SmallIntegerField(default=0)
    notes_on_authors = models.TextField(blank=True, null=True)
    addressees_as_marked = models.TextField(blank=True, null=True)
    addressees_inferred = models.SmallIntegerField(default=0)
    addressees_uncertain = models.SmallIntegerField(default=0)
    notes_on_addressees = models.TextField(blank=True, null=True)
    destination_id = models.IntegerField(blank=True, null=True)
    # destination = models.ForeignKey('CofkCollectDestinationOfWork', models.CASCADE, blank=True, null=True)
    destination_as_marked = models.TextField(blank=True, null=True)
    destination_inferred = models.SmallIntegerField(default=0)
    destination_uncertain = models.SmallIntegerField(default=0)
    origin_id = models.IntegerField(blank=True, null=True)
    # origin = models.ForeignKey('CofkCollectOriginOfWork', models.CASCADE, blank=True, null=True)
    origin_as_marked = models.TextField(blank=True, null=True)
    origin_inferred = models.SmallIntegerField(default=0)
    origin_uncertain = models.SmallIntegerField(default=0)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    language_of_work = models.CharField(max_length=255, blank=True, null=True)
    incipit = models.TextField(blank=True, null=True)
    excipit = models.TextField(blank=True, null=True)
    accession_code = models.CharField(max_length=250, blank=True, null=True)
    notes_on_letter = models.TextField(blank=True, null=True)
    notes_on_people_mentioned = models.TextField(blank=True, null=True)
    upload_status = models.ForeignKey(CofkCollectStatus, models.SET_NULL,
                                      db_column='upload_status', null=True)
    editors_notes = models.TextField(blank=True, null=True)
    _id = models.CharField(db_column='_id', max_length=32, blank=True,
                           null=True)  # Field renamed because it started with '_'.
    date_of_work2_approx = models.SmallIntegerField(default=0)
    date_of_work2_inferred = models.SmallIntegerField(default=0)
    date_of_work2_uncertain = models.SmallIntegerField(default=0)
    mentioned_as_marked = models.TextField(blank=True, null=True)
    mentioned_inferred = models.SmallIntegerField(default=0)
    mentioned_uncertain = models.SmallIntegerField(default=0)
    notes_on_destination = models.TextField(blank=True, null=True)
    notes_on_origin = models.TextField(blank=True, null=True)
    notes_on_place_mentioned = models.TextField(blank=True, null=True)
    place_mentioned_as_marked = models.TextField(blank=True, null=True)
    place_mentioned_inferred = models.SmallIntegerField(default=0)
    place_mentioned_uncertain = models.SmallIntegerField(default=0)
    upload_name = models.CharField(max_length=254, blank=True, null=True)
    explicit = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_work'
        unique_together = (('upload', 'iwork_id'),)

    # def __str__(self):
    #   return f'Work #{self.iwork_id}'

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

    @property
    def display_issues(self) -> str:
        return '\n'.join([self.display_date_issues, self.display_origin_issues, self.display_destination_issues,
                         self.display_authors_issues, self.display_addressees_issues, self.display_mentioned_issues])


class CofkCollectAddresseeOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    addressee_id = models.IntegerField()
    iperson = models.ForeignKey('uploader.CofkCollectPerson', models.CASCADE)
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='addressees')
    notes_on_addressee = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.iperson)

    class Meta:
        db_table = 'cofk_collect_addressee_of_work'
        unique_together = (('upload', 'iwork_id', 'addressee_id'),)


class CofkCollectAuthorOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    author_id = models.IntegerField()
    iperson = models.ForeignKey('uploader.CofkCollectPerson', models.CASCADE, related_name='author_of')
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='authors')
    notes_on_author = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_author_of_work'
        unique_together = (('upload', 'iwork_id', 'author_id'),)


class CofkCollectDestinationOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    destination_id = models.IntegerField()
    location = models.ForeignKey('uploader.CofkCollectLocation', models.CASCADE)
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='destination')
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
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='languages')
    language_code = models.ForeignKey('core.Iso639LanguageCode', models.CASCADE, db_column='language_code', )
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.language_code)

    class Meta:
        db_table = 'cofk_collect_language_of_work'
        unique_together = (('upload', 'iwork_id', 'language_of_work_id'),)


class CofkCollectOriginOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    origin_id = models.IntegerField()
    location = models.ForeignKey('uploader.CofkCollectLocation', models.CASCADE)
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='origin')
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
    iperson = models.ForeignKey('uploader.CofkCollectPerson', models.CASCADE)
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='people_mentioned')
    notes_on_person_mentioned = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return str(self.iperson)

    class Meta:
        db_table = 'cofk_collect_person_mentioned_in_work'
        unique_together = (('upload', 'iwork_id', 'mention_id'),)


class CofkCollectPlaceMentionedInWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    mention_id = models.IntegerField()
    location = models.ForeignKey('uploader.CofkCollectLocation', models.CASCADE)
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='places_mentioned')
    notes_on_place_mentioned = models.TextField(blank=True, null=True)
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_place_mentioned_in_work'
        unique_together = (('upload', 'iwork_id', 'mention_id'),)


class CofkCollectSubjectOfWork(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    subject_of_work_id = models.IntegerField()
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='subjects')
    subject = models.ForeignKey('core.CofkUnionSubject', models.CASCADE)

    class Meta:
        db_table = 'cofk_collect_subject_of_work'
        unique_together = (('upload', 'iwork_id', 'subject_of_work_id'),)


class CofkCollectWorkResource(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    resource_id = models.IntegerField()
    iwork = models.ForeignKey('uploader.CofkCollectWork', models.CASCADE, related_name='resources')
    resource_name = models.TextField()
    resource_details = models.TextField()
    resource_url = models.TextField()
    _id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_work_resource'
        unique_together = (('upload', 'iwork_id', 'resource_id'),)
