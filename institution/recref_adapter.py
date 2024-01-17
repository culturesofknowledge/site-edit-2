from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from core.helper.common_recref_adapter import TargetResourceRecrefAdapter, TargetImageRecrefAdapter
from . import models


class InstResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: models.CofkUnionInstitution = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkinstitutionresourcemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return models.CofkInstitutionResourceMap.institution

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return models.CofkInstitutionResourceMap.resource


class InstImageRecrefAdapter(TargetImageRecrefAdapter):

    def __init__(self, parent):
        self.parent: models.CofkUnionInstitution = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkinstitutionimagemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return models.CofkInstitutionImageMap.institution

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return models.CofkInstitutionImageMap.image
