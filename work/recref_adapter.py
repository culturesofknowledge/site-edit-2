from abc import ABC
from typing import Type

from core.helper import model_serv
from core.helper.common_recref_adapter import RecrefFormAdapter, TargetCommentRecrefAdapter, \
    TargetResourceRecrefAdapter, TargetImageRecrefAdapter
from core.models import Recref, CofkUnionSubject
from institution import inst_serv
from institution.models import CofkUnionInstitution
from location import location_serv
from location.models import CofkUnionLocation
from manifestation import manif_serv
from manifestation.models import CofkUnionManifestation, CofkManifInstMap, CofkManifManifMap, CofkManifCommentMap, \
    CofkManifImageMap
from work import work_serv
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkSubjectMap, CofkWorkWorkMap, CofkWorkCommentMap, \
    CofkWorkResourceMap


class WorkLocRecrefAdapter(RecrefFormAdapter):
    def __init__(self, parent=None):
        self.parent: CofkUnionWork = parent

    def find_target_display_name_by_id(self, target_id):
        return location_serv.get_recref_display_name(self.find_target_instance(target_id))

    def recref_class(self) -> Type[Recref]:
        return CofkWorkLocationMap

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionLocation, location_id=target_id)

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkWorkLocationMap
        recref.work = parent
        recref.location = target

    def find_recref_records(self, rel_type):
        return self.parent.cofkworklocationmap_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'location_id'


class ManifInstRecrefAdapter(RecrefFormAdapter):
    def __init__(self, parent=None):
        self.parent: CofkUnionManifestation = parent

    def find_target_display_name_by_id(self, target_id):
        return inst_serv.get_recref_display_name(self.find_target_instance(target_id))

    def recref_class(self) -> Type[Recref]:
        return CofkManifInstMap

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionInstitution, institution_id=target_id)

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkManifInstMap
        recref.manif = parent
        recref.inst = target

    def find_recref_records(self, rel_type):
        return self.parent.cofkmanifinstmap_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'inst_id'


class WorkSubjectRecrefAdapter(RecrefFormAdapter):
    def __init__(self, parent=None):
        self.parent: CofkUnionSubject = parent

    def find_target_display_name_by_id(self, target_id):
        s = self.find_target_instance(target_id)
        return s and s.subject_desc

    def recref_class(self) -> Type[Recref]:
        return CofkWorkSubjectMap

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionSubject, subject_id=target_id)

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkWorkSubjectMap
        recref.work = parent
        recref.subject = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkworksubjectmap_set, rel_type)

    def target_id_name(self):
        return 'subject_id'


class WorkWorkRecrefAdapter(RecrefFormAdapter, ABC):

    def find_target_display_name_by_id(self, target_id):
        return work_serv.get_recref_display_name(CofkUnionWork.objects.get(work_id=target_id))

    def recref_class(self) -> Type[Recref]:
        return CofkWorkWorkMap

    def find_target_instance(self, target_id):
        return CofkUnionWork.objects.get(work_id=target_id)


class EarlierLetterRecrefAdapter(WorkWorkRecrefAdapter):
    def __init__(self, work=None):
        self.work = work

    def set_parent_target_instance(self, recref, parent, target):
        recref.work_from = parent
        recref.work_to = target

    def find_recref_records(self, rel_type):
        return self.work.work_from_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'work_to_id'


class LaterLetterRecrefAdapter(WorkWorkRecrefAdapter):
    def __init__(self, work=None):
        self.work = work

    def set_parent_target_instance(self, recref, parent, target):
        recref.work_from = target
        recref.work_to = parent

    def find_recref_records(self, rel_type):
        return self.work.work_to_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'work_from_id'


class ManifManifRecrefAdapter(RecrefFormAdapter, ABC):

    def find_target_display_name_by_id(self, target_id):
        return manif_serv.get_recref_display_name(self.find_target_instance(target_id))

    def recref_class(self) -> Type[Recref]:
        return CofkManifManifMap

    def find_target_instance(self, target_id):
        return CofkUnionManifestation.objects.get(pk=target_id)


class EnclosureManifRecrefAdapter(ManifManifRecrefAdapter):
    def __init__(self, manif=None):
        self.manif: CofkUnionManifestation = manif

    def set_parent_target_instance(self, recref, parent, target):
        recref.manif_from = parent
        recref.manif_to = target

    def find_recref_records(self, rel_type):
        return self.manif.manif_from_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'manif_to_id'


class EnclosedManifRecrefAdapter(ManifManifRecrefAdapter):
    def __init__(self, manif=None):
        self.manif: CofkUnionManifestation = manif

    def set_parent_target_instance(self, recref, parent, target):
        recref.manif_from = target
        recref.manif_to = parent

    def find_recref_records(self, rel_type):
        return self.manif.manif_to_set.filter(relationship_type=rel_type).iterator()

    def target_id_name(self):
        return 'manif_from_id'


class WorkCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionWork = parent

    def recref_class(self) -> Type[Recref]:
        return CofkWorkCommentMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkWorkCommentMap
        recref.work = parent
        recref.comment = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkworkcommentmap_set, rel_type)


class ManifCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionManifestation = parent

    def recref_class(self) -> Type[Recref]:
        return CofkManifCommentMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkManifCommentMap
        recref.manifestation = parent
        recref.comment = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkmanifcommentmap_set, rel_type)


class WorkResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionWork = parent

    def recref_class(self) -> Type[Recref]:
        return CofkWorkResourceMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkWorkResourceMap
        recref.work = parent
        recref.resource = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkworkresourcemap_set, rel_type)


class ManifImageRecrefAdapter(TargetImageRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionManifestation = parent

    def recref_class(self) -> Type[Recref]:
        return CofkManifImageMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkManifImageMap
        recref.manif = parent
        recref.image = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofkmanifimagemap_set, rel_type)
