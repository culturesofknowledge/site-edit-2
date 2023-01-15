import functools
from typing import Iterable

from django.db import models

from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_COMMENT_DATE, \
    REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO, REL_TYPE_CREATED
from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref, CofkLookupCatalogue

SEQ_NAME_COFKUNIONWORK__IWORK_ID = 'cofk_union_work_iwork_id_seq'


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
    original_catalogue = models.ForeignKey("core.CofkLookupCatalogue", models.DO_NOTHING,
                                           db_column='original_catalogue', blank=True, null=False,
                                           to_field='catalogue_code',
                                           default='',
                                           db_constraint=False, )
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

    def find_people_by_rel_type(self, rel_type) -> Iterable['CofkWorkPersonMap']:
        return self.cofkworkpersonmap_set.filter(relationship_type=rel_type).all()

    @property
    def creators_for_display(self):
        creators = self.find_people_by_rel_type(REL_TYPE_CREATED)
        if len(creators) > 0:
            return ",".join([str(c.person) for c in creators])
        else:
            return ''

    @property
    def places_from_for_display(self):
        if self.origin_location:
            return str(self.origin_location.location)
        return ''

    @property
    def places_to_for_display(self):
        if self.destination_location:
            return str(self.destination_location.location)
        return ''

    @property
    def addressees_for_display(self):
        addressees = self.find_people_by_rel_type(REL_TYPE_COMMENT_ADDRESSEE)
        if len(addressees) > 0:
            return ",".join([str(a.person) for a in addressees])
        else:
            return ''


class CofkWorkCommentMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_comment_map'


class CofkWorkResourceMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_resource_map'


class CofkWorkWorkMap(Recref):
    work_from = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE,
                                  related_name='work_from_set', )
    work_to = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE,
                                related_name='work_to_set', )

    class Meta(Recref.Meta):
        db_table = 'cofk_work_work_map'


class CofkWorkSubjectMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    subject = models.ForeignKey("core.CofkUnionSubject", on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_subject_map'


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


class CofkUnionLanguageOfWork(models.Model):
    lang_work_id = models.AutoField(primary_key=True)
    work = models.ForeignKey(CofkUnionWork, models.DO_NOTHING, related_name='language_set')
    language_code = models.ForeignKey('core.Iso639LanguageCode', models.DO_NOTHING,
                                      db_column='language_code',
                                      to_field='code_639_3',
                                      )
    notes = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_language_of_work'
        unique_together = (('work', 'language_code'),)


class CofkUnionQueryableWork(models.Model):
    iwork_id = models.IntegerField(primary_key=True)
    work = models.OneToOneField('CofkUnionWork', models.DO_NOTHING, related_name='queryable')
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

    @property
    def catalogue(self) -> str:
        return CofkLookupCatalogue.objects.filter(catalogue_code=self.original_catalogue)[0].catalogue_name


