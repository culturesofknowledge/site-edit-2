from typing import Iterable, Optional

from django.db import models

from core.constant import REL_TYPE_STORED_IN, REL_TYPE_ENCLOSED_IN
from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref, CofkLookupDocumentType


class CofkManifCommentMap(Recref):
    manifestation = models.ForeignKey('manifestation.CofkUnionManifestation', on_delete=models.CASCADE)
    comment = models.ForeignKey('core.CofkUnionComment', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_comment_map'


class CofkManifPersonMap(Recref):
    manifestation = models.ForeignKey('manifestation.CofkUnionManifestation', on_delete=models.CASCADE)
    person = models.ForeignKey('person.CofkUnionPerson', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_person_map'


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
    manifestation_creation_date_is_range = models.SmallIntegerField()
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
    work = models.ForeignKey('work.CofkUnionWork', models.CASCADE, null=True)
    images = models.ManyToManyField(to='core.CofkUnionImage', through='CofkManifImageMap')

    class Meta:
        db_table = 'cofk_union_manifestation'

    def find_comments_by_rel_type(self, rel_type) -> Iterable['CofkUnionComment']:
        return (r.comment for r in self.cofkmanifcommentmap_set.filter(relationship_type=rel_type))

    def find_selected_inst(self) -> Optional['CofkManifInstMap']:
        return self.cofkmanifinstmap_set.filter(relationship_type=REL_TYPE_STORED_IN).first()

    def find_enclosed_in(self):
        return self.manif_from_set.filter(relationship_type=REL_TYPE_ENCLOSED_IN).all()

    def find_encloses(self):
        return self.manif_to_set.filter(relationship_type=REL_TYPE_ENCLOSED_IN).all()

    def to_string(self):
        manifestation_summary = ''

        if doctype := CofkLookupDocumentType.objects.filter(document_type_code=self.manifestation_type).first():
            manifestation_summary += f'{doctype.document_type_desc}. '
        else:
            manifestation_summary += f'{self.manifestation_type}. '

        if self.postage_marks:
            manifestation_summary += f'Postmark: {self.postage_marks}. '

        if manif_inst := self.find_selected_inst():
            manifestation_summary += manif_inst.inst.institution_name

        if manif_inst and self.id_number_or_shelfmark:
            manifestation_summary += ': '

        if self.id_number_or_shelfmark:
            manifestation_summary += self.id_number_or_shelfmark

        if self.manifestation_incipit:
            manifestation_summary +=  f'\n ~ Incipit: {self.manifestation_incipit}. '

        if self.manifestation_excipit:
            manifestation_summary +=  f'\n ~ Excipit: {self.manifestation_excipit}. '

        for enclosed_in in self.find_enclosed_in():
            manifestation_summary += f'\n ~ {enclosed_in.id_number_or_shelfmark}'

        for encloses in self.find_encloses():
            manifestation_summary += f'\n ~ {encloses.id_number_or_shelfmark}'

        return manifestation_summary


class CofkUnionLanguageOfManifestation(models.Model):
    lang_manif_id = models.AutoField(primary_key=True)
    manifestation = models.ForeignKey(CofkUnionManifestation, models.DO_NOTHING,
                                      related_name='language_set')
    language_code = models.ForeignKey('core.Iso639LanguageCode', models.DO_NOTHING,
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


class CofkManifInstMap(Recref):
    manif = models.ForeignKey(CofkUnionManifestation,
                              on_delete=models.CASCADE)
    inst = models.ForeignKey("institution.CofkUnionInstitution",
                             on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_inst_map'


class CofkManifImageMap(Recref):
    manif = models.ForeignKey(CofkUnionManifestation, on_delete=models.CASCADE)
    image = models.ForeignKey('core.CofkUnionImage', on_delete=models.CASCADE)

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_image_map'


