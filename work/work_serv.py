import logging
from datetime import date
from typing import Any, List

from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO, \
    REL_TYPE_MENTION
from core.helper import data_serv
from location import location_serv
from person import person_serv
from work.models import CofkUnionWork

log = logging.getLogger(__name__)
HIDDEN_DATE_STD = '1900-01-01'


def get_recref_display_name(work: CofkUnionWork) -> str:
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


def join_names(names) -> str:
    return ' ~ '.join(names)


def find_related_person_names(work: CofkUnionWork, rel_type):
    return (person_serv.get_recref_display_name(r.person)
            for r in work.cofkworkpersonmap_set.filter(relationship_type=rel_type))


def find_related_location_names(work: CofkUnionWork, rel_type):
    return (location_serv.get_recref_display_name(r.location)
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


def get_checked_form_url_by_pk(pk):
    if work := CofkUnionWork.objects.get(pk=pk):
        return reverse('work:full_form', args=[work.iwork_id])

    log.warning('get form url failed, work not found [%s]', pk)
    return ''


def get_display_id(work: CofkUnionWork):
    return work and work.iwork_id


class DisplayableWork(CofkUnionWork):
    """
    Wrapper for display work
    """

    class Meta:
        proxy = True

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
        origin = ''
        if self.origin_location:
            origin = str(self.origin_location)

        if self.origin_as_marked:
            origin += f'\n\nAs marked: {self.origin_as_marked}'

        return origin

    @property
    def places_to_for_display(self) -> str:
        destination = ''
        if self.destination_location:
            destination = str(self.destination_location)

        if self.destination_as_marked:
            destination += f'\n\nAs marked: {self.destination_as_marked}'

        return destination

    @property
    def manifestations_for_display(self) -> List[str]:
        # Derived value for CofkUnionQueryable
        # Example:
        # Letter.Bodleian Library, University of Oxford: MS.Locke c. 19, f. 48 - - Printed copy. ‘The Clarendon Edition of the Works of John Locke: The Correspondence of John Locke’, ed.E.S.de Beer, 8 vols(Oxford: OUP, 1978), vol. 4, letter 1282.
        # see https://github.com/culturesofknowledge/site-edit/blob/9a74580d2567755ab068a2d8761df8f81718910e/docker-postgres/cofk-empty.postgres.schema.sql#L6541
        manif_names = [m.to_string() for m in self.manif_set.all()]
        return manif_names

    @property
    def images(self) -> str:
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
    def related_works(self) -> str:
        links = [
            data_serv.endcode_url_content(
                reverse("work:overview_form", args=[t.work_from.iwork_id]),
                t.work_from.description,
            ) for t in (self.work_to_set.all() or [])
        ]
        return ', '.join(links)

    @property
    def related_resources(self) -> str:
        links = [
            data_serv.endcode_url_content(
                r.resource.resource_url,
                r.resource.resource_name,
            ) for r in (self.cofkworkresourcemap_set.all() or [])
        ]
        return ', '.join(links)

    @property
    def other_details(self) -> str:
        _other_details = []

        if self.keywords:
            _other_details.append(f'<strong>Keywords</strong>: {self.keywords}')

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
    def language_of_work(self) -> str:
        return ", ".join([format_language(l) for l in self.language_set.all()])

    @property
    def general_notes(self) -> str:
        return ', '.join([c.comment for c in self.general_comments])

    @property
    def catalogue(self) -> str:
        if original_catalogue := self.original_catalogue:
            return original_catalogue.catalogue_name
        return ''

    @property
    def subjects_for_display(self) -> str:
        # Derived value for CofkUnionQueryable
        return ", ".join([s.subject_desc for s in self.subjects.all()])


def format_language(lang: 'CofkUnionLanguageOfWork') -> str:
    if lang.notes:
        return f'{lang.language_code.language_name} ({lang.notes})'
    return lang.language_code.language_name


def flags(work: CofkUnionWork) -> str:
    tooltip = []

    if work.date_of_work_inferred or work.date_of_work_uncertain:
        if work.date_of_work_inferred:
            tooltip.append('Date of work INFERRED')

        if work.date_of_work_uncertain:
            tooltip.append('Date of work UNCERTAIN')

        if work.date_of_work_as_marked:
            tooltip.append(f'(Date of work as marked: {work.date_of_work_as_marked})')

    if work.origin_inferred or work.origin_uncertain:
        if work.origin_inferred:
            tooltip.append('Origin INFERRED')

        if work.origin_uncertain:
            tooltip.append('Origin UNCERTAIN')

        if work.origin_as_marked:
            tooltip.append(f'(Origin as marked: {work.origin_as_marked})')

    if work.authors_inferred or work.authors_uncertain:
        if work.authors_inferred:
            tooltip.append('Author INFERRED')

        if work.authors_uncertain:
            tooltip.append('Author UNCERTAIN')

        if work.authors_as_marked:
            tooltip.append(f'(Author as marked: {work.authors_as_marked})')

    if work.addressees_inferred or work.addressees_uncertain:
        if work.addressees_inferred:
            tooltip.append('Addressee INFERRED')

        if work.addressees_uncertain:
            tooltip.append('Addressee UNCERTAIN')

        if work.addressees_as_marked:
            tooltip.append(f'(Addressee as marked: {work.addressees_as_marked})')

    if work.destination_inferred or work.destination_uncertain:
        if work.destination_inferred:
            tooltip.append('Destination INFERRED')

        if work.destination_uncertain:
            tooltip.append('Destination UNCERTAIN')

        if work.destination_as_marked:
            tooltip.append(f'(Destination as marked: {work.destination_as_marked})')

    return ', '.join(tooltip)


def q_hidden_works(prefix=None, check_hidden_date=True) -> Q:
    """
    In original EMLO edit, there have three methods to hide work record
    * work_to_be_deleted = 1
    * related original_catalogue of work is not published
    * date_of_work_std = '1900-01-01'
    """
    if prefix:
        prefix = prefix + '__'
    else:
        prefix = ''

    q = (
            Q(**{prefix + 'work_to_be_deleted': 1})
            | Q(**{prefix + 'original_catalogue__publish_status': 0})
    )
    if check_hidden_date:
        q |= Q(**{prefix + 'date_of_work_std': HIDDEN_DATE_STD})
    return q


def q_visible_works(prefix=None, check_hidden_date=True, check_published=False) -> Q:
    if prefix:
        prefix = prefix + '__'
    else:
        prefix = ''
    q = Q(**{prefix + 'work_to_be_deleted': 0})

    if check_published:
        q &= (
                Q(**{prefix + 'original_catalogue__isnull': True})
                | Q(**{prefix + 'original_catalogue__publish_status': 1})
        )

    if check_hidden_date:
        q &= ~Q(**{prefix + 'date_of_work_std': HIDDEN_DATE_STD})
    return q


def is_hidden_work(work: CofkUnionWork, cached_catalogue_status: dict[Any, int] = None) -> bool:
    if work is None:
        return True

    if cached_catalogue_status:
        is_catalogue_published = cached_catalogue_status.get(work.original_catalogue_id, False)
    else:
        is_catalogue_published = work.original_catalogue is not None and work.original_catalogue.publish_status

    return (work.work_to_be_deleted or
            not is_catalogue_published or
            work.date_of_work_std == HIDDEN_DATE_STD)
