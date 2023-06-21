from typing import Iterable, Optional

from django.db import models

from core.constant import REL_TYPE_STORED_IN, REL_TYPE_ENCLOSED_IN
from core.helper import model_utils, recref_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref


class CofkManifCommentMap(Recref):
    manifestation = models.ForeignKey('manifestation.CofkUnionManifestation', on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_comment_map'
        indexes = [
            models.Index(fields=['manifestation', 'relationship_type']),
        ]


class CofkManifPersonMap(Recref):
    manifestation = models.ForeignKey('manifestation.CofkUnionManifestation', on_delete=models.CASCADE)
    person = models.ForeignKey('person.CofkUnionPerson', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_person_map'
        indexes = [
            models.Index(fields=['manifestation', 'relationship_type']),
        ]


class CofkUnionManifestation(models.Model, RecordTracker):
    manifestation_id = models.CharField(primary_key=True, max_length=100)
    manifestation_type = models.CharField(max_length=3, default='')
    id_number_or_shelfmark = models.CharField(max_length=500, blank=True, null=True)
    printed_edition_details = models.TextField(blank=True, null=True)
    paper_size = models.CharField(max_length=500, blank=True, null=True)
    paper_type_or_watermark = models.CharField(max_length=500, blank=True, null=True)
    number_of_pages_of_document = models.IntegerField(blank=True, null=True)
    number_of_pages_of_text = models.IntegerField(blank=True, null=True)
    seal = models.CharField(max_length=500, blank=True, null=True)
    postage_marks = models.CharField(max_length=500, blank=True, null=True)
    endorsements = models.TextField(blank=True, null=True)
    non_letter_enclosures = models.TextField(blank=True, null=True)
    manifestation_creation_calendar = models.CharField(max_length=2, default='U')
    manifestation_creation_date = models.DateField(blank=True, null=True)
    manifestation_creation_date_gregorian = models.DateField(blank=True, null=True)
    manifestation_creation_date_year = models.IntegerField(blank=True, null=True)
    manifestation_creation_date_month = models.IntegerField(blank=True, null=True)
    manifestation_creation_date_day = models.IntegerField(blank=True, null=True)
    manifestation_creation_date_inferred = models.SmallIntegerField(default=0)
    manifestation_creation_date_uncertain = models.SmallIntegerField(default=0)
    manifestation_creation_date_approx = models.SmallIntegerField(default=0)
    manifestation_is_translation = models.SmallIntegerField(default=0)
    language_of_manifestation = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    manifestation_incipit = models.TextField(blank=True, null=True)
    manifestation_excipit = models.TextField(blank=True, null=True)
    manifestation_ps = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    creation_user = models.CharField(max_length=50)
    change_timestamp = models.DateTimeField(blank=True, null=True, default=model_utils.default_current_timestamp)
    change_user = models.CharField(max_length=50)
    manifestation_creation_date2_year = models.IntegerField(blank=True, null=True)
    manifestation_creation_date2_month = models.IntegerField(blank=True, null=True)
    manifestation_creation_date2_day = models.IntegerField(blank=True, null=True)
    manifestation_creation_date_is_range = models.SmallIntegerField(default=0)
    manifestation_creation_date_as_marked = models.CharField(max_length=250, blank=True, null=True)
    opened = models.CharField(max_length=3, default='o')
    uuid = models.UUIDField(blank=True, null=True)
    routing_mark_stamp = models.TextField(blank=True, null=True)
    routing_mark_ms = models.TextField(blank=True, null=True)
    handling_instructions = models.TextField(blank=True, null=True)
    stored_folded = models.CharField(max_length=20, blank=True, null=True)
    postage_costs_as_marked = models.CharField(max_length=500, blank=True, null=True)
    postage_costs = models.CharField(max_length=500, blank=True, null=True)
    non_delivery_reason = models.CharField(max_length=500, blank=True, null=True)
    date_of_receipt_as_marked = models.CharField(max_length=500, blank=True, null=True)
    manifestation_receipt_calendar = models.CharField(max_length=2)
    manifestation_receipt_date = models.DateField(blank=True, null=True)
    manifestation_receipt_date_gregorian = models.DateField(blank=True, null=True)
    manifestation_receipt_date_year = models.IntegerField(blank=True, null=True)
    manifestation_receipt_date_month = models.IntegerField(blank=True, null=True)
    manifestation_receipt_date_day = models.IntegerField(blank=True, null=True)
    manifestation_receipt_date_inferred = models.SmallIntegerField(default=0)
    manifestation_receipt_date_uncertain = models.SmallIntegerField(default=0)
    manifestation_receipt_date_approx = models.SmallIntegerField(default=0)
    manifestation_receipt_date2_year = models.IntegerField(blank=True, null=True)
    manifestation_receipt_date2_month = models.IntegerField(blank=True, null=True)
    manifestation_receipt_date2_day = models.IntegerField(blank=True, null=True)
    manifestation_receipt_date_is_range = models.SmallIntegerField(default=0)
    accompaniments = models.TextField(blank=True, null=True)

    # relation
    work = models.ForeignKey('work.CofkUnionWork', models.CASCADE, null=True, related_name='manif_set')
    images = models.ManyToManyField(to='core.CofkUnionImage', through='CofkManifImageMap')
    comments = models.ManyToManyField(to='core.CofkUnionComment', through='CofkManifCommentMap')

    @property
    def inst(self) -> 'CofkUnionInstitution':
        inst = self.cofkmanifinstmap_set.first()
        inst = inst and inst.inst
        return inst

    class Meta:
        db_table = 'cofk_union_manifestation'

    def find_comments_by_rel_type(self, rel_type) -> Iterable['CofkUnionComment']:
        return (r.comment for r in recref_utils.prefetch_filter_rel_type(self.cofkmanifcommentmap_set, rel_type))

    def find_selected_inst(self) -> Optional['CofkManifInstMap']:
        return next(recref_utils.prefetch_filter_rel_type(self.cofkmanifinstmap_set, REL_TYPE_STORED_IN), None)

    def find_enclosed_in(self):
        return (mm.manif_to for mm in recref_utils.prefetch_filter_rel_type(self.manif_from_set, REL_TYPE_ENCLOSED_IN))

    def find_encloses(self):
        return (mm.manif_from for mm in recref_utils.prefetch_filter_rel_type(self.manif_to_set, REL_TYPE_ENCLOSED_IN))

    def to_string(self):
        from manifestation import manif_utils
        return '\n'.join(manif_utils.get_manif_details(self))


class CofkUnionLanguageOfManifestation(models.Model):
    lang_manif_id = models.AutoField(primary_key=True)
    manifestation = models.ForeignKey(CofkUnionManifestation, models.CASCADE,
                                      related_name='language_set')
    language_code = models.ForeignKey('core.Iso639LanguageCode', models.CASCADE,
                                      db_column='language_code',
                                      to_field='code_639_3')
    notes = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_language_of_manifestation'
        unique_together = (('manifestation', 'language_code'),)


class CofkManifManifMap(Recref):
    manif_from = models.ForeignKey(CofkUnionManifestation, on_delete=models.CASCADE,
                                   related_name='manif_from_set', )
    manif_to = models.ForeignKey(CofkUnionManifestation, on_delete=models.CASCADE,
                                 related_name='manif_to_set', )

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_manif_map'
        indexes = [
            models.Index(fields=['manif_from', 'relationship_type']),
            models.Index(fields=['manif_to', 'relationship_type']),
        ]


class CofkManifInstMap(Recref):
    manif = models.ForeignKey(CofkUnionManifestation,
                              on_delete=models.CASCADE,
                              related_name='cofkmanifinstmap_set', )
    inst = models.ForeignKey("institution.CofkUnionInstitution",
                             on_delete=models.CASCADE, )

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_inst_map'
        indexes = [
            models.Index(fields=['manif', 'relationship_type']),
        ]


class CofkManifImageMap(Recref):
    manif = models.ForeignKey(CofkUnionManifestation, on_delete=models.CASCADE)
    image = models.ForeignKey('core.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_image_map'
        indexes = [
            models.Index(fields=['manif', 'relationship_type']),
        ]
