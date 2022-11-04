from datetime import date

from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO
from location import location_utils
from person import person_utils
from work.models import CofkUnionWork


def get_recref_display_name(work: CofkUnionWork):
    if not work:
        return ''

    if all((work.date_of_work_std_year,
            work.date_of_work_std_month,
            work.date_of_work_std_day,)):
        work_date = date(year=work.date_of_work_std_year,
                         month=work.date_of_work_std_month,
                         day=work.date_of_work_std_day)
        work_date_str = work_date.strftime('%-d %b %Y')
    else:
        work_date_str = 'Unknown date'

    from_person_str = find_related_person_as_display_name(work.cofkworkpersonmap_set, REL_TYPE_CREATED)
    from_person_str = from_person_str or 'unknown author/sender'
    to_person_str = find_related_person_as_display_name(work.cofkworkpersonmap_set, REL_TYPE_WAS_ADDRESSED_TO)
    to_person_str = to_person_str or 'unknown addressee'

    from_location_str = find_related_location_as_display_name(work.cofkworklocationmap_set, REL_TYPE_WAS_SENT_FROM)
    to_location_str = find_related_location_as_display_name(work.cofkworklocationmap_set, REL_TYPE_WAS_SENT_TO)

    return f'{work_date_str}: {from_person_str}{from_location_str} to {to_person_str}{to_location_str}'


def find_related_person_as_display_name(related_manager, rel_type):
    return ' ~ '.join(
        person_utils.get_recref_display_name(r.person)
        for r in related_manager.filter(relationship_type=rel_type)
    )


def find_related_location_as_display_name(related_manager, rel_type):
    name = ' ~ '.join(
        location_utils.get_recref_display_name(r.location)
        for r in related_manager.filter(relationship_type=rel_type)
    )
    if name:
        name = f'({name})'
    else:
        name = ''
    return name


def get_recref_target_id(work: CofkUnionWork):
    return work and work.work_id
