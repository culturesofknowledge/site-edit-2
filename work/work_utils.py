import datetime
import logging
import warnings
from datetime import date

from django.urls import reverse
from django.utils.safestring import mark_safe

from core import constant
from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO, \
    REL_TYPE_MENTION
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
    warnings.warn('queryable_work is deprecated', DeprecationWarning)
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
    queryable_work.creators_searchable = work.queryable_people(REL_TYPE_CREATED, is_details=True)
    queryable_work.addressees_for_display = work.queryable_people(REL_TYPE_WAS_ADDRESSED_TO)
    queryable_work.addressees_searchable = work.queryable_people(REL_TYPE_WAS_ADDRESSED_TO, is_details=True)

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


class DisplayableWork:
    """
    Wrapper for display work
    """

    def __init__(self, work):
        self.work = work

    def __getattr__(self, item):
        return getattr(self.work, item)

    @property
    def date_for_ordering(self):
        date_list = []
        if self.date_of_work_std_year:
            date_list.append(str(self.date_of_work_std_year))

        if self.date_of_work_std_month:
            date_list.append(str(self.date_of_work_std_month))

        if self.date_of_work_std_day:
            date_list.append(str(self.date_of_work_std_day))

        return '-'.join(date_list)

    @property
    def creators_for_display(self):
        return self.queryable_people(REL_TYPE_CREATED)

    @property
    def addressees_for_display(self):
        return self.queryable_people(REL_TYPE_WAS_ADDRESSED_TO)

    @property
    def places_from_for_display(self) -> str:
        # Derived value for CofkUnionQueryable
        if self.origin_location:
            return str(self.origin_location)
        return ''

    @property
    def places_to_for_display(self) -> str:
        # Derived value for CofkUnionQueryable
        if self.destination_location:
            return str(self.destination_location)
        return ''

    @property
    def manifestations_for_display(self):
        # Derived value for CofkUnionQueryable
        # Example:
        # Letter.Bodleian Library, University of Oxford: MS.Locke c. 19, f. 48 - - Printed copy. ‘The Clarendon Edition of the Works of John Locke: The Correspondence of John Locke’, ed.E.S.de Beer, 8 vols(Oxford: OUP, 1978), vol. 4, letter 1282.
        # see https://github.com/culturesofknowledge/site-edit/blob/9a74580d2567755ab068a2d8761df8f81718910e/docker-postgres/cofk-empty.postgres.schema.sql#L6541
        manifestations = self.manif_set.all()
        if len(manifestations) > 0:
            return ", ".join([str(m.to_string()) for m in manifestations])
        else:
            return ''

    @property
    def images(self):
        start = 'xxxCofkImageIDStartxxx'
        end = 'xxxCofkImageIDEndxxx'

        manifestations = self.manif_set.all()
        images = []
        if len(manifestations) > 0:
            for m in manifestations:
                images.extend(list(m.images.all()))

        return ", ".join(f'{start}{i.image_filename}{end}' for i in images)

    def queryable_people(self, rel_type: str, is_details: bool = False) -> str:
        # Derived value for CofkUnionQueryable
        return ", ".join([p.to_string(is_details=is_details) for p in self.find_persons_by_rel_type(rel_type)])

    @property
    def people_mentioned(self):
        return self.queryable_people(REL_TYPE_MENTION)

    @property
    def related_resources(self):
        '''
        This field combines related resources and related works.
        '''
        start = 'xxxCofkLinkStartxxx'
        end = 'xxxCofkLinkEndxxx'
        start_href = 'xxxCofkHrefStartxxx'
        end_href = 'xxxCofkHrefEndxxx'
        resources = ''

        if to_works := self.work_to_set.all():
            resources += ", ".join([
                f'{start}{start_href}{reverse("work:overview_form", args=[t.work_from.iwork_id])}{end_href}{t.work_from.description}{end}'
                for t in to_works])

        if linked_resources := self.cofkworkresourcemap_set.all():
            resources += ", ".join(
                [f'{start}{start_href}{r.resource.resource_url}{end_href}{r.resource.resource_name}{end}' for r in
                 linked_resources])

        return resources

    @property
    def other_details(self):
        _other_details = []

        if self.abstract:
            _other_details.append(f'<strong>Abstract</strong>: {self.abstract}')

        language_of_work = self.language_of_work
        if language_of_work:
            label = 'Languages' if len(language_of_work.split(',')) else 'Language'
            _other_details.append(f'<strong>{label}</strong>: {language_of_work}')

        if general_notes := self.general_notes:
            _other_details.append(f'<strong>Notes</strong>: {general_notes}')

        if people_mentioned := self.people_mentioned:
            _other_details.append(f'<strong>People mentioned</strong>: {people_mentioned}')

        return mark_safe('<br/><br/>'.join(_other_details))

    @property
    def language_of_work(self):
        return ", ".join([format_language(l) for l in self.language_set.iterator()])

    @property
    def general_notes(self):
        return ', '.join([c.comment for c in self.general_comments])

    @property
    def catalogue(self) -> str:
        if original_catalogue := self.original_catalogue:
            return original_catalogue.catalogue_name
        return ''


def format_language(lang: 'CofkUnionLanguageOfWork') -> str:
    if lang.notes:
        return f'{lang.language_code.language_name} ({lang.notes})'
    return lang.language_code.language_name
