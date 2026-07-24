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
from core.helper.recref_serv import get_left_right_rel_obj, find_relationship_type
from core.models import CofkUnionComment, CofkUnionRelationshipType, CofkUnionResource, Recref, \
    CofkUnionNationality, CofkUnionImage, CofkUnionRoleCategory, CofkUnionSubject
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation, CofkUnionLanguageOfManifestation
from person.models import CofkUnionPerson
from publication.models import CofkUnionPublication
from work.models import CofkUnionWork, CofkUnionLanguageOfWork

log = logging.getLogger(__name__)


_NO_OLD_NOTES = object()


def handle_non_triggered_record(sender: ModelBase, instance: models.Model, is_create: bool | None = True,
                                old_notes=_NO_OLD_NOTES):
    """
    Some records like CofkUnionLanguageOfWork, will not create audit record when created by DB trigger.
    This function will create audit record for such records.

    Parameters
    ----------
    sender
    instance
    is_create
        True for a newly added language row, False for a removed one, None for
        an in-place edit to an existing row's notes (no language added/removed)
    old_notes
        for is_create=None only: this row's notes value before the edit, so the
        "old" side of the audit record can be reconstructed even though the DB
        row already reflects the new note by the time this runs

    Returns
    -------

    """
    def _format_lang_entry(name, notes):
        return f'{name} ({notes})' if notes else name

    def _to_column_value(entries):
        return ', '.join(sorted(_format_lang_entry(name, notes) for name, notes in entries))

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

    # column_name
    if isinstance(instance, CofkUnionLanguageOfWork):
        column_name = 'language_of_work'
    elif isinstance(instance, CofkUnionLanguageOfManifestation):
        column_name = 'language_of_manifestation'
    else:
        raise NotImplementedError(f'unsupported instance type {instance}')

    # only coalesce with a recent audit row for this *same* column -- without the
    # column_name filter this would also match (and overwrite) an unrelated audit
    # row for the same manifestation written moments earlier in the same save
    # (e.g. the "manifestation_is_translation" checkbox), destroying that record.
    org_audit = CofkUnionAuditLiteral.objects.filter(
        change_timestamp__gt=django.utils.timezone.now() - datetime.timedelta(seconds=30),
        table_name=table_name,
        key_value_integer=key_value_integer,
        column_name=column_name,
    ).first()

    _languages = []
    if isinstance(instance, CofkUnionLanguageOfWork):
        _languages = instance.work.language_set.all()
    elif isinstance(instance, CofkUnionLanguageOfManifestation):
        _languages = instance.manifestation.language_set.all()
    cur_entries = {(l.language_code.language_name, l.notes) for l in _languages}
    new_column_value = _to_column_value(cur_entries)
    if org_audit:
        # update existing audit for language change
        org_audit.new_column_value = new_column_value
        org_audit.save()
        return

    # prepare for new audit record for language change

    changed_entry = (instance.language_code.language_name, instance.notes)

    if is_create:
        org_entries = cur_entries - {changed_entry}
    elif is_create is None:
        # in-place note edit: same languages, just this row's note reverts
        old_notes = None if old_notes is _NO_OLD_NOTES else old_notes
        org_entries = (cur_entries - {changed_entry}) | {(changed_entry[0], old_notes)}
    else:
        org_entries = cur_entries | {changed_entry}

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
        old_column_value=_to_column_value(org_entries),
    )


def handle_update_language_notes(sender: ModelBase, instance: models.Model):
    """pre_save: capture a language row's notes value before it's overwritten,
    so handle_non_triggered_record can still build the "old" audit value for an
    in-place note edit (no language added/removed) once post_save fires --
    without this, such an edit currently produces no audit record at all, since
    handle_non_triggered_record is otherwise only invoked on create/delete.
    """
    if sender not in {
        CofkUnionLanguageOfWork,
        CofkUnionLanguageOfManifestation,
    }:
        return

    if not instance.pk:
        return  # this is a create, not an update -- handled on post_save instead

    old_instance = model_serv.get_safe(sender, pk=instance.pk)
    if old_instance is not None and old_instance.notes != instance.notes:
        instance.old_notes_for_audit = old_instance.notes



def build_recref_key_decode(instance: Recref, adapters) -> str:
    """'X was former owner of Y' style sentence describing a recref, using the
    relationship type's own left-to-right description as the connecting verb.
    """
    left_adapter, right_adapter = adapters
    rel_type = find_relationship_type(instance.relationship_type)
    verb = rel_type.desc_left_to_right if rel_type else instance.relationship_type
    return f'{left_adapter.key_decode()} {verb} {right_adapter.key_decode()}'


def save_audit_records(instance: Recref, old_instance: Recref = None, ):
    adapters = get_left_right_adapters(instance)
    columns = ['from_date', 'to_date']

    if old_instance is not None:
        columns = (c for c in columns
                   if getattr(instance, c, None) != getattr(old_instance, c, None))
    else:
        columns = (c for c in columns
                   if getattr(instance, c, None) is not None)

    key_decode = build_recref_key_decode(instance, adapters)

    for column_name in columns:
        # handle date fields
        literal = CofkUnionAuditLiteral(
            change_user=getattr(instance, 'change_user', constant.DEFAULT_CHANGE_USER),
            change_type=constant.CHANGE_TYPE_NEW if old_instance is None else constant.CHANGE_TYPE_CHANGE,
            table_name=instance._meta.db_table,
            key_value_text=' '.join(adapter.key_value_text() for adapter in adapters),
            key_value_integer=instance.recref_id,
            key_decode=key_decode,
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
    """add "Relation: " New records to cofk_union_audit_literal for a newly
    created relationship. Only call this when the relationship was actually
    just created (e.g. from post_save with created=True) - it does not
    diff against a previous state, so calling it on every save would write
    spurious duplicate "New" rows for what are really just date edits on an
    already-existing relationship (see save_audit_records for that case).
    """
    _write_relation_audit_pair(sender, instance, constant.CHANGE_TYPE_NEW)


def add_relation_audit_to_literal_on_delete(sender: ModelBase, instance: models.Model):
    """add "Relation: " Del records to cofk_union_audit_literal for a
    relationship that was just removed (e.g. unticking a role checkbox,
    removing a location/related-person entry). Mirrors
    add_relation_audit_to_literal but for the opposite event - see that
    function's docstring for why deletion needed its own entry point rather
    than reusing insert's code path unconditionally.
    """
    _write_relation_audit_pair(sender, instance, constant.CHANGE_TYPE_DELETE)


def _write_relation_audit_pair(sender: ModelBase, instance: models.Model, change_type: str):
    """
    add "Relation: " records to cofk_union_audit_literal
    """

    if not issubclass(sender, Recref):
        return

    instance: Recref

    try:
        # define left, right column
        left_rel_obj, right_rel_obj = get_left_right_rel_obj(instance)

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
                change_type=change_type,
                table_name=cur_left_rel._meta.db_table,
                key_value_text=left_adapter.key_value_text(),
                key_value_integer=instance.recref_id,
                key_decode=left_adapter.key_decode(),
                column_name=f'Relationship: {rel_desc}',
            )
            if change_type == constant.CHANGE_TYPE_DELETE:
                literal.old_column_value = right_adapter.key_decode()
            else:
                literal.new_column_value = right_adapter.key_decode()
            literal.save()
    except Exception:
        # e.g. the related record (person/location/role...) on either side
        # is itself mid-cascade-delete (this recref row being removed as a
        # side effect of deleting its parent) and no longer resolvable -
        # audit logging must never block the actual data change
        log.exception(f'failed to write relationship audit record [{instance}][{change_type}]')
