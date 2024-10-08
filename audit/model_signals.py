import datetime
import logging

import django
from django.db import models
from django.db.models.base import ModelBase

from audit import audit_recref_adapter
from audit.audit_recref_adapter import AuditRecrefAdapter
from audit.models import CofkUnionAuditLiteral
from core import constant
from core.helper import model_serv
from core.helper.recref_serv import get_left_right_rel_obj
from core.models import CofkUnionComment, CofkUnionRelationshipType, CofkUnionResource, Recref, \
    CofkUnionNationality, CofkUnionImage, CofkUnionRoleCategory, CofkUnionSubject
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation, CofkUnionLanguageOfManifestation
from person.models import CofkUnionPerson
from publication.models import CofkUnionPublication
from work.models import CofkUnionWork, CofkUnionLanguageOfWork

log = logging.getLogger(__name__)


def handle_non_triggered_record(sender: ModelBase, instance: models.Model, is_create: bool = True):
    """
    Some records like CofkUnionLanguageOfWork, will not create audit record when created by DB trigger.
    This function will create audit record for such records.

    Parameters
    ----------
    sender
    instance
    is_create

    Returns
    -------

    """
    def _to_column_value(names):
        return ', '.join(sorted(names))

    if sender not in {
        CofkUnionLanguageOfWork,
        CofkUnionLanguageOfManifestation,
    }:
        return


    # parent_instance
    if isinstance(instance, CofkUnionLanguageOfWork):
        parent_instance = instance.work
    elif isinstance(instance, CofkUnionLanguageOfManifestation):
        parent_instance = instance.manifestation
    else:
        raise NotImplementedError(f'unsupported instance type {instance}')

    audit_adapter = to_audit_adapter(parent_instance)
    table_name = parent_instance._meta.db_table
    key_value_integer = audit_adapter.key_value_integer()

    org_audit = CofkUnionAuditLiteral.objects.filter(
        change_timestamp__gt=django.utils.timezone.now() - datetime.timedelta(seconds=30),
        table_name=table_name,
        key_value_integer=key_value_integer,
    ).first()

    _languages = []
    if isinstance(instance, CofkUnionLanguageOfWork):
        _languages = instance.work.language_set.all()
    elif isinstance(instance, CofkUnionLanguageOfManifestation):
        _languages = instance.manifestation.language_set.all()
    cur_lang_names = {l.language_code.language_name for l in _languages}
    new_column_value = _to_column_value(cur_lang_names)
    if org_audit:
        # update existing audit for language change
        org_audit.new_column_value = new_column_value
        org_audit.save()
        return

    # prepare for new audit record for language change

    changed_lang_name = instance.language_code.language_name

    if is_create:
        org_lang_names = cur_lang_names - {changed_lang_name}
    else:
        org_lang_names = cur_lang_names | {changed_lang_name}

    # column_name
    if isinstance(instance, CofkUnionLanguageOfWork):
        column_name = 'language_of_work'
    elif isinstance(instance, CofkUnionLanguageOfManifestation):
        column_name = 'language_of_manifestation'
    else:
        raise NotImplementedError(f'unsupported instance type {instance}')

    CofkUnionAuditLiteral.objects.create(
        change_timestamp=model_serv.default_current_timestamp(),
        change_user=parent_instance.change_user,
        change_type=constant.CHANGE_TYPE_CHANGE,
        table_name=table_name,
        key_value_text=audit_adapter.key_value_text(),
        key_value_integer=key_value_integer,
        key_decode=audit_adapter.key_decode(),
        column_name=column_name,
        new_column_value=new_column_value,
        old_column_value=_to_column_value(org_lang_names),
    )


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
        CofkUnionRelationshipType,
        CofkUnionResource,
        # CofkUnionRoleCategory,   # have no change_user
        # CofkUnionSubject,         # have no change_user
        CofkUnionWork,
    }:
        return

    if not (change_user := getattr(instance, 'change_user', None)):
        log.warning(f'skip update audit user, {sender} has no [{change_user}] ')
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
            change_type=constant.CHANGE_TYPE_NEW if old_instance is None else constant.CHANGE_TYPE_CHANGE,
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


def get_left_right_adapters(instance: Recref):
    left_right_instances = get_left_right_rel_obj(instance)
    adapters = [to_audit_adapter(i) for i in left_right_instances]
    return adapters


def handle_update_recref_date(sender: ModelBase, instance: models.Model):
    if not issubclass(sender, Recref):
        return

    if instance.pk is None or not (old_instance := model_serv.get_safe(sender, pk=instance.pk)):
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

    # define left, right column
    left_rel_obj, right_rel_obj = get_left_right_rel_obj(instance)

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
