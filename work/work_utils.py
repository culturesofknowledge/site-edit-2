import datetime
import logging
from datetime import date

from django.urls import reverse

from core import constant
from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO
from core.helper import model_utils
from core.models import CofkLookupCatalogue
from location import location_utils
from person import person_utils
from siteedit2.utils.log_utils import log_no_url
from work.models import CofkUnionWork, CofkUnionQueryableWork

log = logging.getLogger(__name__)


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

    return f'{work_date_str}: {from_person_str} {from_location_str} to {to_person_str} {to_location_str}'


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


def _get_original_catalogue_val(work: CofkUnionWork, field_name):
    if work.original_catalogue_id:
        return work.original_catalogue.catalogue_code
    else:
        cat = CofkLookupCatalogue.objects.filter(catalogue_code='').first()
        return cat.catalogue_code if cat else ''


special_clone_fields = {
    'original_catalogue': _get_original_catalogue_val,
    'date_of_work_std': lambda w, n: datetime.datetime.strptime(
        w.date_of_work_std or constant.DEFAULT_EMPTY_DATE_STR,
        constant.STD_DATE_FORMAT).date(),
}


def _get_clone_value_default(work: CofkUnionWork, field_name):
    return getattr(work, field_name)


def _get_clone_value(work: CofkUnionWork, field_name):
    val_fn = special_clone_fields.get(field_name, _get_clone_value_default)
    return val_fn(work, field_name)


def clone_queryable_work(work: CofkUnionWork, reload=False, _return=False):
    if work is None:
        log.debug('skip clone_queryable_work work is None')
        return

    if reload:
        work = reload_work(work)

    exclude_fields = ['iwork_id', 'subjects']
    queryable_work = model_utils.get_safe(
        CofkUnionQueryableWork, iwork_id=work.iwork_id
    ) or CofkUnionQueryableWork()

    queryable_field_names = {field for field in dir(CofkUnionQueryableWork) if field not in exclude_fields}
    work_field_names = (field.name for field in work._meta.get_fields()
                        if hasattr(field, 'column'))
    common_field_names = (name for name in work_field_names
                          if name in queryable_field_names)
    field_val_list = ((name, _get_clone_value(work, name)) for name in common_field_names)
    updated_field_val_list = ((name, val) for name, val in field_val_list
                              if getattr(queryable_work, name) != val)
    updated_field_dict = dict(updated_field_val_list)
    for name, val in updated_field_dict.items():
        setattr(queryable_work, name, val)

    queryable_work.iwork_id = work.iwork_id
    # People
    queryable_work.creators_for_display = work.queryable_people(REL_TYPE_CREATED)
    queryable_work.creators_searchable = work.queryable_people(REL_TYPE_CREATED, searchable=True)
    queryable_work.addressees_for_display = work.queryable_people(REL_TYPE_WAS_ADDRESSED_TO)
    queryable_work.addressees_searchable = work.queryable_people(REL_TYPE_WAS_ADDRESSED_TO, searchable=True)

    # Places
    queryable_work.places_from_for_display = work.places_from_for_display
    queryable_work.places_from_searchable = queryable_work.places_from_for_display
    queryable_work.places_to_for_display = work.places_to_for_display
    queryable_work.places_to_searchable = queryable_work.places_to_for_display

    queryable_work.manifestations_for_display = work.manifestations_for_display
    queryable_work.subjects = work.queryable_subjects
    queryable_work.language_of_work = work.languages
    queryable_work.related_resources = work.resources
    queryable_work.images = work.images
    # queryable_work.flags = exclamation(queryable_work)

    if _return:
        return queryable_work

    queryable_work.save()
    log.info(f'queryable_work saved. [{work.iwork_id}][{list(updated_field_dict.keys())}]  ')


def reload_work(work: CofkUnionWork) -> CofkUnionWork | None:
    return CofkUnionWork.objects.filter(pk=work.pk).first()


def get_display_id(work: CofkUnionWork | CofkUnionQueryableWork):
    return work and work.iwork_id
