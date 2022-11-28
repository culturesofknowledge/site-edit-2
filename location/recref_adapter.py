from typing import Type

from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, TargetResourceRecrefAdapter, \
    TargetImageRecrefAdapter
from core.models import Recref
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap, CofkLocationImageMap
from uploader.models import CofkUnionImage


class LocationCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def recref_class(self) -> Type[Recref]:
        return CofkLocationCommentMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkLocationCommentMap
        recref.location = parent
        recref.comment = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationcommentmap_set, rel_type)


class LocationResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def recref_class(self) -> Type[Recref]:
        return CofkLocationResourceMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkLocationResourceMap
        recref.location = parent
        recref.resource = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationresourcemap_set, rel_type)


class LocationImageRecrefAdapter(TargetImageRecrefAdapter):

    def __init__(self, parent):
        self.parent: CofkUnionImage = parent

    def recref_class(self) -> Type[Recref]:
        return CofkLocationImageMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkLocationImageMap
        recref.location = parent
        recref.image = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationimagemap_set, rel_type)
