from institution.models import CofkInstitutionImageMap, CofkInstitutionResourceMap
from location.models import CofkLocationCommentMap, CofkLocationResourceMap
from person.models import CofkPersonLocationMap, CofkPersonPersonMap, CofkPersonCommentMap, CofkPersonResourceMap, \
    CofkPersonImageMap

from work import models as work_models
from manifestation import models as manif_models

recref_left_right_pairs = [
    # Location
    (CofkLocationCommentMap.comment, CofkLocationCommentMap.location),
    (CofkLocationResourceMap.location, CofkLocationResourceMap.resource),

    # Person
    (CofkPersonLocationMap.person, CofkPersonLocationMap.location),
    (CofkPersonPersonMap.person, CofkPersonPersonMap.related),
    (CofkPersonCommentMap.comment, CofkPersonCommentMap.person),
    (CofkPersonResourceMap.person, CofkPersonResourceMap.resource),
    (CofkPersonImageMap.image, CofkPersonImageMap.person),

    # Repositories
    (CofkInstitutionImageMap.image, CofkInstitutionImageMap.institution),
    (CofkInstitutionResourceMap.institution, CofkInstitutionResourceMap.resource),

    # Work
    (work_models.CofkWorkCommentMap.comment, work_models.CofkWorkCommentMap.work),
    (work_models.CofkWorkResourceMap.work, work_models.CofkWorkResourceMap.resource),
    (work_models.CofkWorkWorkMap.work_from, work_models.CofkWorkWorkMap.work_to),
    (work_models.CofkWorkSubjectMap.work, work_models.CofkWorkSubjectMap.subject),
    (work_models.CofkWorkPersonMap.work, work_models.CofkWorkPersonMap.person),
    (work_models.CofkWorkLocationMap.work, work_models.CofkWorkLocationMap.location),

    # manif
    (manif_models.CofkManifManifMap.manif_from, manif_models.CofkManifManifMap.manif_to),
    (manif_models.CofkManifCommentMap.comment, manif_models.CofkManifCommentMap.manifestation),
    (manif_models.CofkManifPersonMap.person, manif_models.CofkManifPersonMap.manifestation),
    (manif_models.CofkManifInstMap.manif, manif_models.CofkManifInstMap.inst),
    (manif_models.CofkManifImageMap.image, manif_models.CofkManifImageMap.manif),

]
