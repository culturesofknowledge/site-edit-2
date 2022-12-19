from abc import ABC
from typing import Type

from core.helper import model_utils
from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, TargetResourceRecrefAdapter, \
    RecrefFormAdapter, TargetPersonRecrefAdapter, TargetImageRecrefAdapter, TargetLocationRecrefAdapter
from core.models import Recref, CofkUnionRoleCategory
from person.models import CofkUnionPerson, CofkPersonCommentMap, CofkPersonResourceMap, CofkPersonRoleMap, \
    CofkPersonPersonMap, CofkPersonImageMap, CofkPersonLocationMap


class PersonLocRecrefAdapter(TargetLocationRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonLocationMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonLocationMap
        recref.person = parent
        recref.location = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonlocationmap_set, rel_type)


class PersonCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonCommentMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonCommentMap
        recref.person = parent
        recref.comment = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersoncommentmap_set, rel_type)


class PersonResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonResourceMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonResourceMap
        recref.person = parent
        recref.resource = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonresourcemap_set, rel_type)


class PersonImageRecrefAdapter(TargetImageRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonImageMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonImageMap
        recref.person = parent
        recref.image = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonimagemap_set, rel_type)


class PersonRoleRecrefAdapter(RecrefFormAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def find_target_display_name_by_id(self, target_id):
        target = self.find_target_instance(target_id)
        return target and target.role_category_desc

    def recref_class(self) -> Type[Recref]:
        return CofkPersonRoleMap

    def find_target_instance(self, target_id):
        return model_utils.get_safe(CofkUnionRoleCategory, pk=target_id)

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonRoleMap
        recref.person = parent
        recref.role = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonrolemap_set, rel_type)

    def target_id_name(self):
        return 'role_id'


class PersonPersonRecrefAdapter(TargetPersonRecrefAdapter, ABC):
    def __init__(self, parent=None):
        self.parent: CofkUnionPerson = parent

    def recref_class(self) -> Type[Recref]:
        return CofkPersonPersonMap


class ActivePersonRecrefAdapter(PersonPersonRecrefAdapter):

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonPersonMap
        recref.person = parent
        recref.related = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.active_relationships, rel_type)

    def target_id_name(self):
        return 'related_id'


class PassivePersonRecrefAdapter(PersonPersonRecrefAdapter):

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkPersonPersonMap
        recref.person = target
        recref.related = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.passive_relationships, rel_type)

    def target_id_name(self):
        return 'person_id'
