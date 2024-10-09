from django.db import models
from django.urls import reverse

from core import constant
from core.helper import data_serv
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person import person_serv


class AuditRecrefAdapter:

    def __init__(self, instance: models.Model):
        self.instance = instance

    def key_value_text(self):
        return str(self.instance.pk)

    def key_value_integer(self):
        return self.key_value_text()

    def key_decode(self, is_expand_details=False):
        """ replacement of db function dbf_cofk_union_decode """
        return f'Empty or missing value in {self.instance._meta.db_table} with key {self.key_value_text()}'


class LocationAuditAdapter(AuditRecrefAdapter):

    def key_decode(self, is_expand_details=False):
        self.instance: CofkUnionLocation
        if is_expand_details:
            synonyms = ''
            if self.instance.location_synonyms:
                synonyms = f' ({self.instance.location_synonyms})'

            return f"{self.instance.location_name}{synonyms}"
        else:
            return self.instance.location_name


class PersonAuditAdapter(AuditRecrefAdapter):

    def key_value_integer(self):
        return self.instance.iperson_id

    def key_decode(self, is_expand_details=False):
        return person_serv.decode_person(self.instance, is_expand_details=is_expand_details)


class ResourceAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.resource_name


class WorkAuditAdapter(AuditRecrefAdapter):
    def key_value_text(self):
        return self.instance.work_id

    def key_value_integer(self):
        return self.instance.iwork_id

    def key_decode(self, is_expand_details=False):
        return data_serv.endcode_url_content(
            reverse("work:overview_form", args=[self.instance.iwork_id]),
            self.instance.description
        )


class ManifAuditAdapter(AuditRecrefAdapter):

    def key_value_integer(self):
        return None

    def key_decode(self, is_expand_details=False):
        self.instance: CofkUnionManifestation

        decode = self.instance.id_number_or_shelfmark or ''
        decode += ' '
        decode += self.instance.printed_edition_details or ''
        date = self.instance.manifestation_creation_date
        if date or date != constant.STD_DATE_FORMAT:
            if self.instance.manifestation_creation_date_approx:
                date = f'c.{date}'
            if self.instance.manifestation_creation_date_uncertain:
                date = f'{date}?'
            if self.instance.manifestation_creation_date_inferred:
                date = f'[{date}]'
        decode = f'{date}: {decode}'
        return decode


class RelTypeAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.desc_left_to_right


class CommentAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.comment


class ImageAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.image_filename


class InstAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.institution_name


class PubAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.publication_details


class NationalityAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.nationality_desc


class SubjectAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.subject_desc


class RoleCatAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.role_category_desc
