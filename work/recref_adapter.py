from abc import ABC

from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from core.helper.common_recref_adapter import TargetCommentRecrefAdapter, \
    TargetResourceRecrefAdapter, TargetImageRecrefAdapter, FieldsBasedRecrefFormAdapter
from core.models import CofkUnionSubject
from institution import inst_serv
from location import location_serv
from manifestation import manif_serv
from manifestation.models import CofkUnionManifestation, CofkManifInstMap, CofkManifManifMap, CofkManifCommentMap, \
    CofkManifImageMap
from work import work_serv
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkSubjectMap, CofkWorkWorkMap, CofkWorkCommentMap, \
    CofkWorkResourceMap


class WorkLocRecrefAdapter(FieldsBasedRecrefFormAdapter):
    def __init__(self, parent=None):
        self.parent: CofkUnionWork = parent

    def find_target_display_name_by_id(self, target_id):
        return location_serv.get_recref_display_name(self.find_target_instance(target_id))

    def find_recref_records(self, rel_type):
        return self.parent.cofkworklocationmap_set.filter(relationship_type=rel_type).iterator()

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkLocationMap.work

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkLocationMap.location


class ManifInstRecrefAdapter(FieldsBasedRecrefFormAdapter):
    def __init__(self, parent=None):
        self.parent: CofkUnionManifestation = parent

    def find_target_display_name_by_id(self, target_id):
        return inst_serv.get_recref_display_name(self.find_target_instance(target_id))

    def find_recref_records(self, rel_type):
        return self.parent.cofkmanifinstmap_set.filter(relationship_type=rel_type).iterator()

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifInstMap.manif

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifInstMap.inst


class WorkSubjectRecrefAdapter(FieldsBasedRecrefFormAdapter):
    def __init__(self, parent=None):
        self.parent: CofkUnionSubject = parent

    def find_target_display_name_by_id(self, target_id):
        s = self.find_target_instance(target_id)
        return s and s.subject_desc

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkworksubjectmap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkSubjectMap.work

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkSubjectMap.subject


class WorkWorkRecrefAdapter(FieldsBasedRecrefFormAdapter, ABC):

    def find_target_display_name_by_id(self, target_id):
        return work_serv.get_recref_display_name(CofkUnionWork.objects.get(work_id=target_id))


class EarlierLetterRecrefAdapter(WorkWorkRecrefAdapter):
    def __init__(self, work=None):
        self.work = work

    def find_recref_records(self, rel_type):
        return self.work.work_from_set.filter(relationship_type=rel_type).iterator()

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkWorkMap.work_from

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkWorkMap.work_to


class LaterLetterRecrefAdapter(WorkWorkRecrefAdapter):
    def __init__(self, work=None):
        self.work = work

    def find_recref_records(self, rel_type):
        return self.work.work_to_set.filter(relationship_type=rel_type).iterator()

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkWorkMap.work_to

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkWorkMap.work_from


class ManifManifRecrefAdapter(FieldsBasedRecrefFormAdapter, ABC):

    def find_target_display_name_by_id(self, target_id):
        return manif_serv.get_recref_display_name(self.find_target_instance(target_id))


class EnclosureManifRecrefAdapter(ManifManifRecrefAdapter):
    def __init__(self, manif=None):
        self.manif: CofkUnionManifestation = manif

    def find_recref_records(self, rel_type):
        return self.manif.manif_from_set.filter(relationship_type=rel_type).iterator()

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifManifMap.manif_from

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifManifMap.manif_to


class EnclosedManifRecrefAdapter(ManifManifRecrefAdapter):
    def __init__(self, manif=None):
        self.manif: CofkUnionManifestation = manif

    def find_recref_records(self, rel_type):
        return self.manif.manif_to_set.filter(relationship_type=rel_type).iterator()

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifManifMap.manif_to

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifManifMap.manif_from


class WorkCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionWork = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkworkcommentmap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkCommentMap.work

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkCommentMap.comment


class ManifCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionManifestation = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkmanifcommentmap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifCommentMap.manifestation

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifCommentMap.comment


class WorkResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionWork = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkworkresourcemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkResourceMap.work

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkWorkResourceMap.resource


class ManifImageRecrefAdapter(TargetImageRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionManifestation = parent

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkmanifimagemap_set, rel_type)

    @classmethod
    def parent_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifImageMap.manif

    @classmethod
    def target_field(cls) -> ForwardManyToOneDescriptor:
        return CofkManifImageMap.image
