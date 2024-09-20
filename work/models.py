import functools
from typing import Iterable, Union

from django.db import models

from core import constant
from core.constant import REL_TYPE_COMMENT_AUTHOR, REL_TYPE_COMMENT_ADDRESSEE, REL_TYPE_COMMENT_DATE, \
    REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO
from core.helper import model_serv, recref_serv
from core.helper.model_serv import RecordTracker
from core.models import Recref

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
    # language_of_work = models.CharField(max_length=255, blank=True, null=True)
    work_is_translation = models.SmallIntegerField(default=0)
    incipit = models.TextField(blank=True, null=True)
    explicit = models.TextField(blank=True, null=True)
    ps = models.TextField(blank=True, null=True)
    original_catalogue = models.ForeignKey("core.CofkLookupCatalogue", models.DO_NOTHING,
                                           db_column='original_catalogue', blank=True, null=False,
                                           to_field='catalogue_code', default='', db_constraint=False,
                                           related_name='work')
    accession_code = models.CharField(max_length=1000, blank=True, null=True)
    work_to_be_deleted = models.SmallIntegerField(default=0)
    iwork_id = models.IntegerField(
        default=functools.partial(model_serv.next_seq_safe, SEQ_NAME_COFKUNIONWORK__IWORK_ID),
        unique=True,
    )
    editors_notes = models.TextField(blank=True, null=True)
    edit_status = models.CharField(max_length=3, default='')
    relevant_to_cofk = models.CharField(max_length=3, default='Y')
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_serv.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    uuid = models.UUIDField(blank=True, null=True, default=model_serv.default_uuid)
    subjects = models.ManyToManyField(to='core.CofkUnionSubject',
                                      through='CofkWorkSubjectMap', related_name='work', )

    class Meta:
        db_table = 'cofk_union_work'
        permissions = [
            ('export_file', 'Export csv/excel from search results'),
        ]
        indexes = [
            models.Index(fields=['iwork_id']),
        ]

    def find_comments_by_rel_type(self, rel_type) -> Iterable['CofkUnionComment']:
        return (r.comment for r in recref_serv.prefetch_filter_rel_type(self.cofkworkcommentmap_set, rel_type))

    def find_persons_by_rel_type(self, rel_type: str | Iterable) -> Iterable['CofkUnionPerson']:
        return (r.person for r in recref_serv.prefetch_filter_rel_type(self.cofkworkpersonmap_set, rel_type))

    def find_locations_by_rel_type(self, rel_type) -> Iterable['CofkUnionLocation']:
        return (r.location for r in recref_serv.prefetch_filter_rel_type(self.cofkworklocationmap_set, rel_type))

    def find_work_to_list_by_rel_type(self, rel_type) -> Iterable['CofkUnionWork']:
        return (r.work_to for r in recref_serv.prefetch_filter_rel_type(self.work_from_set, rel_type))

    @property
    def author_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(REL_TYPE_COMMENT_AUTHOR)

    @property
    def addressee_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(REL_TYPE_COMMENT_ADDRESSEE)

    @property
    def date_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(REL_TYPE_COMMENT_DATE)

    @property
    def origin_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_ORIGIN)

    @property
    def destination_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_DESTINATION)

    @property
    def route_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_ROUTE)

    @property
    def person_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_PERSON_MENTIONED)

    @property
    def general_comments(self) -> Iterable['CofkUnionComment']:
        return self.find_comments_by_rel_type(constant.REL_TYPE_COMMENT_REFERS_TO)

    @property
    def origin_location(self) -> Union['CofkUnionLocation', None]:
        return next(self.find_locations_by_rel_type(REL_TYPE_WAS_SENT_FROM), None)

    @property
    def destination_location(self) -> Union['CofkUnionLocation', None]:
        return next(self.find_locations_by_rel_type(REL_TYPE_WAS_SENT_TO), None)


class CofkWorkCommentMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_comment_map'
        indexes = [
            models.Index(fields=['work', 'relationship_type']),
        ]


class CofkWorkResourceMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    resource = models.ForeignKey('core.CofkUnionResource', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_resource_map'
        indexes = [
            models.Index(fields=['work', 'relationship_type']),
        ]


class CofkWorkWorkMap(Recref):
    work_from = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE,
                                  related_name='work_from_set', )
    work_to = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE,
                                related_name='work_to_set', )

    class Meta(Recref.Meta):
        db_table = 'cofk_work_work_map'
        indexes = [
            models.Index(fields=['work_from', 'relationship_type']),
            models.Index(fields=['work_to', 'relationship_type']),
        ]


class CofkWorkSubjectMap(Recref):
    work = models.ForeignKey(CofkUnionWork, on_delete=models.CASCADE)
    subject = models.ForeignKey("core.CofkUnionSubject", on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_subject_map'
        indexes = [
            models.Index(fields=['work', 'relationship_type']),
        ]


class CofkWorkPersonMap(Recref):
    """
    possible relationship_type [signed, created, sent], [recipient, intended recipient]
    """
    work = models.ForeignKey(CofkUnionWork,
                             on_delete=models.CASCADE)
    person = models.ForeignKey("person.CofkUnionPerson",
                               on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_person_map'
        indexes = [
            models.Index(fields=['work', 'relationship_type']),
        ]


class CofkWorkLocationMap(Recref):
    work = models.ForeignKey(CofkUnionWork,
                             on_delete=models.CASCADE)
    location = models.ForeignKey("location.CofkUnionLocation",
                                 on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_work_location_map'
        indexes = [
            models.Index(fields=['work', 'relationship_type']),
        ]


class CofkUnionLanguageOfWork(models.Model):
    lang_work_id = models.AutoField(primary_key=True)
    work = models.ForeignKey(CofkUnionWork, models.CASCADE, related_name='language_set')
    language_code = models.ForeignKey('core.Iso639LanguageCode', models.CASCADE,
                                      db_column='language_code',
                                      to_field='code_639_3', )
    notes = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_language_of_work'
        unique_together = (('work', 'language_code'),)
