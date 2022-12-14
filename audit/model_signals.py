import inspect
import logging

from django.db import models
from django.db.models.base import ModelBase

from audit import audit_recref_adapter
from audit.audit_recref_adapter import AuditRecrefAdapter
from audit.models import CofkUnionAuditLiteral
from core import constant, recref_settings
from core.helper import model_utils
from core.models import CofkUnionComment, CofkUnionRelationship, CofkUnionRelationshipType, CofkUnionResource, Recref, \
    CofkUnionNationality
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person.models import CofkUnionPerson
from publication.models import CofkUnionPublication
from uploader.models import CofkUnionImage, CofkUnionSubject, CofkUnionRoleCategory
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


def handle_update_audit_changed_user(sender: ModelBase, instance: models.Model, ):
    """
cofk_aubrey_comment
cofk_aubrey_institution
cofk_aubrey_location
cofk_aubrey_manifestation
cofk_aubrey_person
cofk_aubrey_resource
cofk_aubrey_work
cofk_comenius2_comment
cofk_comenius2_image
cofk_comenius2_institution
cofk_comenius2_location
cofk_comenius2_manifestation
cofk_comenius2_person
cofk_comenius2_resource
cofk_comenius2_work
cofk_union_comment
cofk_union_image
cofk_union_institution
cofk_union_location
cofk_union_manifestation
cofk_union_person
cofk_union_publication
cofk_union_relationship
cofk_union_relationship_type
cofk_union_resource
cofk_union_role_category   # have no change_user
cofk_union_subject         # have no change_user
cofk_union_work
    """

    if sender not in {
        CofkUnionComment,
        CofkUnionImage,
        CofkUnionInstitution,
        CofkUnionLocation,
        CofkUnionManifestation,
        CofkUnionPerson,
        CofkUnionPublication,
        CofkUnionRelationship,
        CofkUnionRelationshipType,
        CofkUnionResource,
        # CofkUnionRoleCategory,   # have no change_user
        # CofkUnionSubject,         # have no change_user
        CofkUnionWork,
    }:
        return

    if not (change_user := getattr(instance, 'change_user', None)):
        log.warning(f'skip update audit user, {sender} has no {change_user} ')
        return

    cond = dict(
        table_name=sender._meta.db_table,
        change_user=constant.DEFAULT_CHANGE_USER,
        key_value_text=str(instance.pk),
    )
    objects_filter = CofkUnionAuditLiteral.objects.filter(**cond)
    if n_audit := objects_filter.count():
        log.debug(f'number of audit records being update {n_audit}')
        objects_filter.update(change_user=change_user)
    else:
        log.warning(f'related audit not found .. {cond}')


def random_choice_left_right(instance: models.Model):
    values = (v for _, v in inspect.getmembers(instance))
    values = [v for v in values if isinstance(v, models.Model)]
    return values[:2]


def save_audit_records(instance: Recref, old_instance: Recref = None, ):
    adapters = get_left_right_adapters(instance)
    columns = ['from_date', 'to_date']

    if old_instance is not None:
        columns = (c for c in columns
                   if getattr(instance, c, None) != getattr(old_instance, c, None))
    else:
        columns = (c for c in columns
                   if getattr(instance, c, None) is not None)

    for column_name in columns:
        # handle date fields
        literal = CofkUnionAuditLiteral(
            change_user=getattr(instance, 'change_user', constant.DEFAULT_CHANGE_USER),
            change_type='New' if old_instance is None else 'Chg',
            table_name=instance._meta.db_table,
            key_value_text=' '.join(adapter.key_value_text() for adapter in adapters),
            key_value_integer=instance.recref_id,
            key_decode=' '.join(adapter.key_decode() for adapter in adapters),
            column_name=column_name,
            new_column_value=getattr(instance, column_name),
        )
        if old_instance is not None:
            literal.old_column_value = getattr(old_instance, column_name)

        literal.save()


def to_audit_adapter(instance: models.Model):
    adapter_map = {
        CofkUnionPerson: audit_recref_adapter.PersonAuditAdapter,
        CofkUnionLocation: audit_recref_adapter.LocationAuditAdapter,
        CofkUnionResource: audit_recref_adapter.ResourceAuditAdapter,
        CofkUnionWork: audit_recref_adapter.WorkAuditAdapter,
        CofkUnionManifestation: audit_recref_adapter.ManifAuditAdapter,
        CofkUnionRelationshipType: audit_recref_adapter.RelTypeAuditAdapter,
        CofkUnionComment: audit_recref_adapter.CommentAuditAdapter,
        CofkUnionImage: audit_recref_adapter.ImageAuditAdapter,
        CofkUnionInstitution: audit_recref_adapter.InstAuditAdapter,
        CofkUnionPublication: audit_recref_adapter.PubAuditAdapter,
        CofkUnionNationality: audit_recref_adapter.NationalityAuditAdapter,
        CofkUnionSubject: audit_recref_adapter.SubjectAuditAdapter,
        CofkUnionRoleCategory: audit_recref_adapter.RoleCatAuditAdapter,
    }

    if adapter := adapter_map.get(instance.__class__):
        return adapter(instance)
    else:
        log.warning(f'undefined audit adapter mapping [{instance}] ')
        return AuditRecrefAdapter(instance)


def get_left_right_adapters(instance):
    # KTODO left right mapping by recref

    log.warning(f'undefined left right mapping for [{instance}]')
    left_right_instances = random_choice_left_right(instance)

    adapters = [to_audit_adapter(i) for i in left_right_instances]
    return adapters


def handle_update_recref_date(sender: ModelBase, instance: models.Model):
    if not issubclass(sender, Recref):
        return

    if instance.pk is None or not (old_instance := model_utils.get_safe(sender, pk=instance.pk)):
        # since pk not exist yet, create audit record created by handle_create_audit_relation for new record
        instance.todo_audit = True
        return

    save_audit_records(instance, old_instance=old_instance)


def handle_create_recref_date(sender: ModelBase, instance: models.Model):
    if not issubclass(sender, Recref) or not getattr(instance, 'todo_audit', False):
        return

    save_audit_records(instance)


def add_relation_audit_to_literal(sender: ModelBase, instance: models.Model):
    """
    add "Relation: " records to cofk_union_audit_literal
    """

    if not issubclass(sender, Recref):
        return

    if sender not in recref_settings.recref_left_right_dict:
        log.warning(f'unknown left right mapping for class [{sender}]')
        return

    # define left, right column
    left_col, right_col = recref_settings.recref_left_right_dict[sender]
    left_rel_obj = left_col.get_object(instance)
    right_rel_obj = right_col.get_object(instance)

    instance: Recref

    # define rel description
    rel_type = CofkUnionRelationshipType.objects.filter(relationship_code=instance.relationship_type).first()
    if rel_type:
        from_left_desc = rel_type.desc_left_to_right
        from_right_desc = rel_type.desc_right_to_left
    else:
        from_left_desc = f'{instance.relationship_type} < '
        from_right_desc = f'{instance.relationship_type} > '

    # save two (both ways) relation audit records
    for cur_left_rel, cur_right_rel, rel_desc in [
        (left_rel_obj, right_rel_obj, from_left_desc),
        (right_rel_obj, left_rel_obj, from_right_desc),
    ]:
        left_adapter = to_audit_adapter(cur_left_rel)
        right_adapter = to_audit_adapter(cur_right_rel)
        literal = CofkUnionAuditLiteral(
            change_user=getattr(instance, 'change_user', constant.DEFAULT_CHANGE_USER),
            change_type='New',
            table_name=cur_left_rel._meta.db_table,
            key_value_text=left_adapter.key_value_text(),
            key_value_integer=instance.recref_id,
            key_decode=left_adapter.key_decode(),
            column_name=f'Relationship: {rel_desc}',
            new_column_value=right_adapter.key_decode(),
        )
        literal.save()
