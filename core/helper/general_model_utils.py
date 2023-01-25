"""
contain method that support multi / general model
"""
from typing import Type

from django.db.models import Model

from core.helper.model_utils import ModelLike
from core.models import CofkUnionComment, CofkUnionResource
from institution import inst_utils
from institution.models import CofkUnionInstitution
from location import location_utils
from location.models import CofkUnionLocation
from manifestation import manif_utils
from manifestation.models import CofkUnionManifestation
from person import person_utils
from person.models import CofkUnionPerson
from work import work_utils
from work.models import CofkUnionWork

ModelOrClass = ModelLike | Type[ModelLike]


def get_model_class_safe(model: ModelOrClass) -> Type[ModelLike]:
    if not model:
        return model
    if isinstance(model, Model):
        return model.__class__
    return model


def get_display_name(model: ModelLike) -> str:
    if not model:
        return ''
    name_fn_map = [
        (CofkUnionLocation, location_utils.get_recref_display_name),
        (CofkUnionPerson, person_utils.get_recref_display_name),
        (CofkUnionWork, work_utils.get_recref_display_name),
        (CofkUnionManifestation, manif_utils.get_recref_display_name),
        (CofkUnionInstitution, inst_utils.get_recref_display_name),
        (CofkUnionComment, lambda c: c and c.comment),
        (CofkUnionResource, lambda c: c and c.resource_name),
    ]

    for c, fn in name_fn_map:
        if isinstance(model, c):
            try:
                return fn(model)
            except Exception:
                pass

    try:
        return f'{model.__class__.__name__}__{model.pk}'
    except Exception:
        return str(model)


def get_name_by_model_class(model_or_class: ModelOrClass) -> str:
    model_class = get_model_class_safe(model_or_class)

    class_name_map = {
        (CofkUnionLocation, 'Location'),
        (CofkUnionPerson, 'Person'),
        (CofkUnionWork, 'Work'),
        (CofkUnionManifestation, 'Manifestation'),
        (CofkUnionInstitution, 'Institution'),
        (CofkUnionComment, 'Comment'),
        (CofkUnionResource, 'Resource'),
    }
    for c, name in class_name_map:
        if c == model_class:
            return name

    return model_class.__name__
