import logging
from abc import ABC
from typing import Type, Iterable

from django.db import models

from core.helper import recref_serv, model_serv
from core.models import Recref, CofkUnionComment, CofkUnionResource, CofkUnionImage
from location import location_serv
from location.models import CofkUnionLocation
from person import person_serv
from person.models import CofkUnionPerson

log = logging.getLogger(__name__)


class RecrefFormAdapter:

    def find_target_display_name_by_id(self, target_id):
        raise NotImplementedError()

    def recref_class(self) -> Type[Recref]:
        raise NotImplementedError()

    def find_target_instance(self, target_id):
        raise NotImplementedError()

    def set_parent_target_instance(self, recref, parent, target):
        raise NotImplementedError()

    def find_recref_records(self, rel_type):
        raise NotImplementedError()

    def target_id_name(self):
        raise NotImplementedError()

    def get_target_id(self, recref: Recref):
        if recref is None:
            return None

        target_id_name = self.target_id_name()
        if not hasattr(recref, target_id_name):
            log.warning(f'target_id_name not found in recref [{target_id_name=}]')
            return None

        return getattr(recref, target_id_name, None)

    def upsert_recref(self, rel_type, parent_instance, target_instance,
                      username=None,
                      org_recref=None,
                      ):
        return recref_serv.upsert_recref(
            rel_type, parent_instance, target_instance,
            create_recref_fn=self.recref_class(),
            set_parent_target_instance_fn=self.set_parent_target_instance,
            username=username,
            org_recref=org_recref,
        )

    def find_recref_records_by_related_manger(self, related_manger, rel_type):
        return related_manger.filter(relationship_type=rel_type).iterator()

    def find_targets_id_list(self, rel_type):
        return (self.get_target_id(r) for r in self.find_recref_records(rel_type))

    def find_all_targets_by_rel_type(self, rel_type) -> Iterable[models.Model]:
        target_id_list = self.find_targets_id_list(rel_type)
        targets = (self.find_target_instance(i) for i in target_id_list)
        return targets

    def find_recref_by_id(self, recref_id):
        return self.recref_class().objects.filter(recref_id=recref_id).first()


class TargetCommentRecrefAdapter(RecrefFormAdapter, ABC):
    def find_target_display_name_by_id(self, target_id):
        c: CofkUnionComment = self.find_target_instance(target_id)
        return c and c.comment

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionComment, comment_id=target_id)

    def target_id_name(self):
        return 'comment_id'


class TargetResourceRecrefAdapter(RecrefFormAdapter, ABC):
    def find_target_display_name_by_id(self, target_id):
        c: CofkUnionResource = self.find_target_instance(target_id)
        return c and c.resource_name

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionResource, resource_id=target_id)

    def target_id_name(self):
        return 'resource_id'


class TargetImageRecrefAdapter(RecrefFormAdapter, ABC):
    def find_target_display_name_by_id(self, target_id):
        c: CofkUnionImage = self.find_target_instance(target_id)
        return c and c.image_filename

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionImage, image_id=target_id)

    def target_id_name(self):
        return 'image_id'


class TargetPersonRecrefAdapter(RecrefFormAdapter, ABC):
    def find_target_display_name_by_id(self, target_id):
        return person_serv.get_recref_display_name(self.find_target_instance(target_id))

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionPerson, person_id=target_id)

    def target_id_name(self):
        return 'person_id'


class TargetLocationRecrefAdapter(RecrefFormAdapter, ABC):
    def find_target_display_name_by_id(self, target_id):
        return location_serv.get_recref_display_name(self.find_target_instance(target_id))

    def find_target_instance(self, target_id):
        return model_serv.get_safe(CofkUnionLocation, location_id=target_id)

    def target_id_name(self):
        return 'location_id'
