from work.models import CofkUnionWork


def get_recref_display_name(work: CofkUnionWork):
    return work and work.work_id  # KTODO


def get_recref_target_id(work: CofkUnionWork):
    return work and work.work_id
