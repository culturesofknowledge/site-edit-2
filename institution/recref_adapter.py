from typing import Type

from core.helper.common_recref_adapter import TargetResourceRecrefAdapter, TargetImageRecrefAdapter
from core.models import Recref
from . import models


class InstResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: models.CofkUnionInstitution = parent

    def recref_class(self) -> Type[Recref]:
        return models.CofkInstitutionResourceMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: models.CofkInstitutionResourceMap
        recref.institution = parent
        recref.resource = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkinstitutionresourcemap_set, rel_type)


class InstImageRecrefAdapter(TargetImageRecrefAdapter):

    def __init__(self, parent):
        self.parent: models.CofkUnionInstitution = parent

    def recref_class(self) -> Type[Recref]:
        return models.CofkInstitutionImageMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: models.CofkInstitutionImageMap
        recref.institution = parent
        recref.image = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkinstitutionimagemap_set, rel_type)
