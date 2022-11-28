from typing import Type

from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, TargetResourceRecrefAdapter
from core.models import Recref
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap


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
