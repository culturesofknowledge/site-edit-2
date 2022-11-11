from datetime import date

from django.urls import reverse

from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO
from location import location_utils
from person import person_utils
from siteedit2.utils.log_utils import log_no_url
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

    from_person_str = join_names(find_related_person_names(work, REL_TYPE_CREATED))
    from_person_str = from_person_str or 'unknown author/sender'
    to_person_str = join_names(find_related_person_names(work, REL_TYPE_WAS_ADDRESSED_TO))
    to_person_str = to_person_str or 'unknown addressee'

    from_location_str = find_related_location_as_display_name(work, REL_TYPE_WAS_SENT_FROM)
    to_location_str = find_related_location_as_display_name(work, REL_TYPE_WAS_SENT_TO)

    return f'{work_date_str}: {from_person_str}{from_location_str} to {to_person_str}{to_location_str}'


def join_names(names):
    return ' ~ '.join(names)


def find_related_person_names(work: CofkUnionWork, rel_type):
    return (person_utils.get_recref_display_name(r.person)
            for r in work.cofkworkpersonmap_set.filter(relationship_type=rel_type))


def find_related_location_names(work: CofkUnionWork, rel_type):
    return (location_utils.get_recref_display_name(r.location)
            for r in work.cofkworklocationmap_set.filter(relationship_type=rel_type))


def find_related_location_as_display_name(work: CofkUnionWork, rel_type):
    name = join_names(find_related_location_names(work, rel_type))
    name = f'({name})' if name else ''
    return name


def get_recref_target_id(work: CofkUnionWork):
    return work and work.work_id


def find_related_comment_names(work: CofkUnionWork, rel_type):
    return (note.comment.comment for note
            in work.cofkworkcommentmap_set.filter(relationship_type=rel_type))


def get_form_url(iwork_id):
    return reverse('work:full_form', args=[iwork_id])


def create_work_id(iwork_id) -> str:
    return f'cofk_union_work-iwork_id:{iwork_id}'


@log_no_url
def get_checked_form_url_by_pk(pk):
    if work := CofkUnionWork.objects.get(pk=pk):
        return reverse('work:full_form', args=[work.iwork_id])
