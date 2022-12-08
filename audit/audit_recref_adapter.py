from django.db import models

from core import constant
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person.models import CofkUnionPerson


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


def decode_is_range_year(year1, year2, is_range):
    if year2 is not None:
        display_year = f'{year2} or before'
    else:
        display_year = f'{year1}'
        if is_range == 1:
            display_year += ' or after'

    return display_year


def decode_person_birth(person: CofkUnionPerson):
    return decode_is_range_year(person.date_of_birth_year, person.date_of_birth2_year,
                                person.date_of_birth_is_range)


def decode_person_death(person: CofkUnionPerson):
    return decode_is_range_year(person.date_of_death_year, person.date_of_death2_year,
                                person.date_of_death_is_range)


class PersonAuditAdapter(AuditRecrefAdapter):

    def key_value_integer(self):
        return self.instance.iperson_id

    def key_decode(self, is_expand_details=False):
        self.instance: CofkUnionPerson
        person = self.instance
        decode = self.instance.foaf_name.strip()

        # organisation
        if person.is_organisation and (org_type := person.organisation_type):
            decode += f' ({org_type.org_type_desc})'

        # Both birth and death dates known
        if (
                (person.date_of_birth_year is not None or person.date_of_birth2_year is not None)
                and (person.date_of_death_year is not None or person.date_of_death2_year is not None)
        ):
            birth_decode = decode_person_birth(person)
            death_decode = decode_person_death(person)
            decode += f', {birth_decode}-{death_decode}'
        elif person.date_of_birth_year is not None or person.date_of_birth2_year is not None:
            # Only birthdate known
            connect_label = ', formed ' if person.is_organisation == 'Y' else ', b.'
            decode += f'{connect_label}{decode_person_birth(person)}'
        elif person.date_of_death_year is not None or person.date_of_death2_year is not None:
            connect_label = ', disbanded ' if person.is_organisation == 'Y' else ', d.'
            decode += f'{connect_label}{decode_person_death(person)}'

        # Flourished dates known
        if person.flourished_year is not None or person.flourished2_year is not None:
            connect_label = ', fl. '

            if person.flourished_year is not None and person.flourished2_year is not None:
                decode += f'{connect_label}{person.flourished_year}-{person.flourished2_year}'
            elif person.flourished_year is not None:
                decode += f'{connect_label}{person.flourished_year}'
                if person.flourished_is_range == 1:
                    decode += ' and after'
            elif person.flourished2_year:
                decode += f'{connect_label} until {person.flourished2_year}'

        # Add alternative names?
        if is_expand_details and self.instance.skos_altlabel:
            decode += '; alternative name(s): ' + self.instance.skos_altlabel

        return decode


class ResourceAuditAdapter(AuditRecrefAdapter):
    def key_decode(self, is_expand_details=False):
        return self.instance.resource_name


class WorkAuditAdapter(AuditRecrefAdapter):
    def key_value_text(self):
        return self.instance.work_id

    def key_value_integer(self):
        return self.instance.iwork_id

    def key_decode(self, is_expand_details=False):
        return self.instance.description


class ManifAuditAdapter(AuditRecrefAdapter):
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
