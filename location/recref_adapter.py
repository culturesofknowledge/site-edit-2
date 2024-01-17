from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, TargetResourceRecrefAdapter, \
    TargetImageRecrefAdapter
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap, CofkLocationImageMap
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, TargetResourceRecrefAdapter, \
    TargetImageRecrefAdapter
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap, CofkLocationImageMap


class LocationCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationcommentmap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkLocationCommentMap.location

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkLocationCommentMap.comment


class LocationResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationresourcemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkLocationResourceMap.location

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkLocationResourceMap.resource


class LocationImageRecrefAdapter(TargetImageRecrefAdapter):

    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationimagemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkLocationImageMap.location

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkLocationImageMap.image
