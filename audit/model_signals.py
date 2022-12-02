import logging

from django.db import models
from django.db.models.base import ModelBase

from audit.models import CofkUnionAuditLiteral
from core.models import CofkUnionComment, CofkUnionRelationship, CofkUnionRelationshipType, CofkUnionResource
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation
from person.models import CofkUnionPerson
from publication.models import CofkUnionPublication
from uploader.models import CofkUnionImage
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
        change_user='__unknown_user',
        key_value_text=str(instance.pk),
    )
    objects_filter = CofkUnionAuditLiteral.objects.filter(**cond)
    if n_audit := objects_filter.count():
        log.debug(f'number of audit records being update {n_audit}')
        objects_filter.update(change_user=change_user)
    else:
        log.warning(f'related audit not found .. {cond}')


def on_update_audit_changed_user(sender: ModelBase, instance: models.Model, created: bool,
                                 raw: bool, using, update_fields, **kwargs):
    handle_update_audit_changed_user(sender, instance)


def on_delete_queryable_work(sender: ModelBase, instance: models.Model, using, **kwargs):
    handle_update_audit_changed_user(sender, instance)
