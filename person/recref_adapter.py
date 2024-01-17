from abc import ABC

from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, TargetResourceRecrefAdapter, \
    TargetPersonRecrefAdapter, TargetImageRecrefAdapter, TargetLocationRecrefAdapter, \
    RecrefFormAdapter
from person.models import CofkUnionPerson, CofkPersonCommentMap, CofkPersonResourceMap, CofkPersonRoleMap, \
    CofkPersonPersonMap, CofkPersonImageMap, CofkPersonLocationMap


class PersonLocRecrefAdapter(TargetLocationRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonlocationmap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonLocationMap.person

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonLocationMap.location


class PersonCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersoncommentmap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonCommentMap.person

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonCommentMap.comment


class PersonResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonresourcemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonResourceMap.person

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonResourceMap.resource


class PersonImageRecrefAdapter(TargetImageRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonimagemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonImageMap.person

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonImageMap.image


class PersonRoleRecrefAdapter(RecrefFormAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionPerson = parent

    def find_target_display_name_by_id(self, target_id):
        target = self.find_target_instance(target_id)
        return target and target.role_category_desc

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkpersonrolemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonRoleMap.person

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonRoleMap.role


class PersonPersonRecrefAdapter(TargetPersonRecrefAdapter, ABC):
    def __init__(self, parent=None):
        self.parent: CofkUnionPerson = parent


class ActivePersonRecrefAdapter(PersonPersonRecrefAdapter):

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.active_relationships, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonPersonMap.person

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonPersonMap.related


class PassivePersonRecrefAdapter(PersonPersonRecrefAdapter):

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.passive_relationships, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonPersonMap.related

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkPersonPersonMap.person
