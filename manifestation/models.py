from typing import Iterable

from django.db import models

from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.models import Recref


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

    class Meta:
        db_table = 'cofk_union_manifestation'

    def find_comments_by_rel_type(self, rel_type) -> Iterable['CofkUnionComment']:
        return (r.comment for r in self.cofkmanifcommentmap_set.filter(relationship_type=rel_type))


class CofkCollectManifestation(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.CASCADE)
    manifestation_id = models.IntegerField()
    iwork = models.ForeignKey('work.CofkCollectWork', models.DO_NOTHING)
    union_manifestation = models.ForeignKey(CofkUnionManifestation, models.DO_NOTHING, blank=True, null=True)
    manifestation_type = models.CharField(max_length=3)
    repository = models.ForeignKey('institution.CofkCollectInstitution', models.DO_NOTHING, blank=True, null=True)
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


class CofkUnionLanguageOfManifestation(models.Model):
    manifestation = models.OneToOneField(CofkUnionManifestation, models.DO_NOTHING, primary_key=True)
    language_code = models.ForeignKey('uploader.Iso639LanguageCode', models.DO_NOTHING, db_column='language_code')
    notes = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'cofk_union_language_of_manifestation'
        unique_together = (('manifestation', 'language_code'),)


class CofkCollectImageOfManif(models.Model):
    upload = models.ForeignKey('uploader.CofkCollectUpload', models.DO_NOTHING)
    manifestation_id = models.IntegerField()
    image_filename = models.CharField(max_length=2000)
    _id = models.CharField(max_length=32, blank=True, null=True)
    iwork_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'cofk_collect_image_of_manif'


class CofkManifManifMap(Recref):
    manif_from = models.ForeignKey(CofkUnionManifestation, on_delete=models.CASCADE,
                                   related_name='manif_from_set', )
    manif_to = models.ForeignKey(CofkUnionManifestation, on_delete=models.CASCADE,
                                 related_name='manif_to_set', )

    class Meta(Recref.Meta):
        db_table = 'cofk_manif_manif_map'


def create_manif_id(iwork_id) -> str:
    return f'W{iwork_id}-{model_utils.next_seq_safe("cofk_union_manif_manif_id_seq")}'
