import logging
from datetime import date
from typing import Any, List
import re

from django.db.models import Q, F
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.constant import REL_TYPE_CREATED, REL_TYPE_WAS_ADDRESSED_TO, REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO, \
    REL_TYPE_MENTION, REL_TYPE_MENTION_PLACE, REL_TYPE_WORK_IS_REPLY_TO, REL_TYPE_WORK_MATCHES
from core.helper import data_serv,query_serv
from core.constant import DEFAULT_MONTH, DEFAULT_DAY, DEFAULT_EMPTY_DATE_STR
from location import location_serv
from person import person_serv
from work.models import CofkUnionWork
from core.helper import query_cache_serv
from manifestation import manif_serv

log = logging.getLogger(__name__)
HIDDEN_DATE_STD = '1900-01-01'




def _format_work_date(year, month, day) -> str:
    if all((year, month, day)):
        return date(year=year, month=month, day=day).strftime('%-d %b %Y')
    elif all((year, month)):
        return date(year=year, month=month, day=1).strftime('%b %Y')
    elif year:
        return str(year)
    return 'Unknown date'


def get_recref_display_name(work: CofkUnionWork) -> str:
    if not work:
        return ''

    work_date_str = _format_work_date(work.date_of_work_std_year,
                                      work.date_of_work_std_month,
                                      work.date_of_work_std_day)

    if work.date_of_work_std_is_range:
        has_from = work.date_of_work_std_year is not None
        has_to = work.date_of_work2_std_year is not None
        if has_from and not has_to:
            work_date_str = f'On or after {work_date_str}'
        elif has_to and not has_from:
            work_date2 = _format_work_date(work.date_of_work2_std_year,
                                           work.date_of_work2_std_month,
                                           work.date_of_work2_std_day)
            work_date_str = f'On or before {work_date2}'
        elif has_from and has_to:
            work_date2 = _format_work_date(work.date_of_work2_std_year,
                                           work.date_of_work2_std_month,
                                           work.date_of_work2_std_day)
            work_date_str = f'{work_date_str} to {work_date2}'

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
        # If there is a "to" date (range), use the "to" date for ordering
        if self.date_of_work2_std_year:
            import calendar
            year = int(self.date_of_work2_std_year)
            # For "to" date, default blank month to 12 (end of year)
            month = int(self.date_of_work2_std_month or 12)
            # Default blank day to last day of the month (handles leap years)
            day = int(self.date_of_work2_std_day or calendar.monthrange(year, month)[1])
            return f"{year:04d}-{month:02d}-{day:02d}"

        # None means the object was not saved; treat as no date
        if self.date_of_work_std is None:
            return DEFAULT_EMPTY_DATE_STR

        # A real date (not the sentinel) can be returned directly
        if self.date_of_work_std != DEFAULT_EMPTY_DATE_STR:
            return self.date_of_work_std

        # Sentinel stored: construct from individual year/month/day fields if available
        if not self.date_of_work_std_year:
            return DEFAULT_EMPTY_DATE_STR

        year = int(self.date_of_work_std_year)
        month = int(self.date_of_work_std_month or DEFAULT_MONTH)
        day = int(self.date_of_work_std_day or DEFAULT_DAY)
        return f"{year:04d}-{month:02d}-{day:02d}"

    @property
    def creators_for_display(self):
        return [p.to_string(is_details=False) for p in self.find_persons_by_rel_type(REL_TYPE_CREATED)]

    @property
    def addressees_for_display(self):
        return [p.to_string(is_details=False) for p in self.find_persons_by_rel_type(REL_TYPE_WAS_ADDRESSED_TO)]

    @property
    def places_from_for_display(self) -> str:
        origin = ''
        if self.origin_location:
            # Base location name
            origin = str(self.origin_location)

        if self.origin_as_marked:
            origin += f'\n\nAs marked: {self.origin_as_marked}'

        return origin

    @property
    def places_to_for_display(self) -> str:
        destination = ''
        if self.destination_location:
            # Base location name
            destination = str(self.destination_location)

        if self.destination_as_marked:
            destination += f'\n\nAs marked: {self.destination_as_marked}'

        return destination

    @property
    def manifestations_for_display(self) -> List[str]:
        manif_type_order = [
            'Letter',
            'Scribal copy',
            'Draft',
            'Extract',
            'Printed copy',
            'Digital copy',
            'Other',
        ]
        manif_type_map = query_cache_serv.create_lookup_doc_desc_map()

        def get_sort_key(manif):
            display_name = manif_type_map.get(manif.manifestation_type, 'Other')
            try:
                return manif_type_order.index(display_name)
            except ValueError:
                return len(manif_type_order)  # Place 'Other' or unknown types at the end

        # Get all manifestations and sort them
        sorted_manifs = sorted(self.manif_set.all(), key=get_sort_key)

        manif_names = [m.to_string() for m in sorted_manifs]
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
        return ' ~ '.join([p.to_string(is_details=is_details) for p in self.find_persons_by_rel_type(rel_type)])

    @property
    def people_mentioned(self):
        return self.queryable_people(REL_TYPE_MENTION)

    @property
    def places_mentioned(self) -> str:
        return ' ~ '.join([l.location_name for l in self.find_locations_by_rel_type(REL_TYPE_MENTION_PLACE) if l.location_name])

    def _work_link_with_id(self, work):
        return data_serv.endcode_url_content(
            reverse("work:overview_form", args=[work.iwork_id]),
            f'[Letter ID: {work.iwork_id}] {work.description}',
        )

    @property
    def related_works(self) -> str:
        sections = []

        # "Reply to" — this work is a reply to earlier letters (work_from_set with is_reply_to)
        reply_to_links = [
            self._work_link_with_id(t.work_to)
            for t in self.work_from_set.filter(relationship_type=REL_TYPE_WORK_IS_REPLY_TO)
        ]
        if reply_to_links:
            sections.append('Reply to: ' + ', '.join(reply_to_links))

        # "Answered by" — later letters that are replies to this work (work_to_set with is_reply_to)
        answered_by_links = [
            self._work_link_with_id(t.work_from)
            for t in self.work_to_set.filter(relationship_type=REL_TYPE_WORK_IS_REPLY_TO)
        ]
        if answered_by_links:
            sections.append('Answered by: ' + ', '.join(answered_by_links))

        # "Matching letter" — bidirectional matches
        matching_links = []
        for t in self.work_from_set.filter(relationship_type=REL_TYPE_WORK_MATCHES):
            matching_links.append(self._work_link_with_id(t.work_to))
        for t in self.work_to_set.filter(relationship_type=REL_TYPE_WORK_MATCHES):
            matching_links.append(self._work_link_with_id(t.work_from))
        if matching_links:
            sections.append('Matching letter: ' + ', '.join(matching_links))

        return ' | '.join(sections)

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

        if places_mentioned := self.places_mentioned:
            _other_details.append(f'<strong>Places mentioned</strong>: {places_mentioned}')

        return mark_safe('<br/><br/>'.join(_other_details))

    @property
    def language_of_work(self) -> str:
        return ", ".join([format_language(l) for l in self.language_set.all()])

    @property
    def general_notes(self) -> str:
        return ' ~ '.join([c.comment for c in self.general_comments])

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

def _is_negated_lookup(lookup_fn) -> bool:
    """Return True if lookup_fn corresponds to a negation search operator."""
    lookup_key = query_serv.get_lookup_key_by_lookup_fn(lookup_fn)
    return lookup_key in ('not_contain', 'not_start_with', 'not_end_with', 'not_equal_to')


def lookup_manifestations_searchable(lookup_fn, field_name: str, value: str) -> Q:
    """
    Allow combining document type and repository (and more terms) using % as an ordered wildcard separator.
    Example: 'Draft%Royal Society' will require manifestations_searchable to contain 'Draft' followed later by
    'Royal Society'. If no % present, fall back to the default lookup function (icontains with wildcard support).
    """
    if not isinstance(value, str):
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    # Use Exists-based optimization for both combined and simple search terms
    # to avoid expensive IRegex on the large aggregated field.
    segments = [seg.strip() for seg in value.split('%') if seg.strip()]
    if not segments:
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    from manifestation.models import CofkUnionManifestation
    from core.models import CofkLookupDocumentType
    from core.constant import REL_TYPE_ENCLOSED_IN
    from django.db.models import Exists, OuterRef

    manif_fields = [
        'postage_marks',
        'cofkmanifinstmap_set__inst__institution_name',
        'id_number_or_shelfmark',
        'printed_edition_details',
        'manifestation_incipit',
        'manifestation_excipit',
    ]

    # Labels used for enclosure relationships – must stay in sync with
    # the prefixes produced by subqueries._prefixed_enclosure_field().
    _ENCLOSURE_LABELS = {
        'had enclosure': 'manif_from_set__manif_to__id_number_or_shelfmark',
        'was enclosed in': 'manif_to_set__manif_from__id_number_or_shelfmark',
    }

    # All segments must match within the SAME manifestation for a work.
    manif_q = Q()
    for segment in segments:
        segment_q = Q()
        for field in manif_fields:
            segment_q |= Q(**{f'{field}__icontains': segment})

        # Check if the segment matches an enclosure label (with or without
        # a trailing shelfmark).  E.g. "Had enclosure" or
        # "Had enclosure: MS 1234".
        seg_lower = segment.lower().strip()
        for label, shelfmark_field in _ENCLOSURE_LABELS.items():
            if label.startswith(seg_lower) or seg_lower.startswith(label):
                # The segment is (part of) an enclosure label – match any
                # manifestation that has the corresponding enclosure
                # relationship.
                enclosure_fk = shelfmark_field.rsplit('__', 2)[0]  # e.g. manif_from_set
                enclosure_q = Q(**{f'{enclosure_fk}__relationship_type': REL_TYPE_ENCLOSED_IN})
                # If the user typed more than just the label (e.g.
                # "Had enclosure: MS 1234"), also filter on the shelfmark.
                extra = seg_lower[len(label):].lstrip(':').strip()
                if extra:
                    enclosure_q &= Q(**{f'{shelfmark_field}__icontains': extra})
                segment_q |= enclosure_q

        # Also search raw enclosure shelfmarks (without label) so that
        # plain shelfmark searches still work.
        segment_q |= Q(**{'manif_from_set__manif_to__id_number_or_shelfmark__icontains': segment})
        segment_q |= Q(**{'manif_to_set__manif_from__id_number_or_shelfmark__icontains': segment})

        segment_q |= Q(manifestation_type__in=CofkLookupDocumentType.objects.filter(
            document_type_desc__icontains=segment
        ).values_list('document_type_code', flat=True))

        manif_q &= segment_q

    exists_q = Exists(CofkUnionManifestation.objects.filter(manif_q, work_id=OuterRef('pk')))
    if _is_negated_lookup(lookup_fn):
        return ~exists_q
    return exists_q


def _parse_person_search_parts(segment: str) -> list:
    """
    Split a person search segment by commas into individual search terms.
    Also recognise date ranges like '1630-1679' and split them into separate
    birth/death year tokens so that each part can be matched independently.

    Name-only parts (non-date) are kept together as a single comma-separated
    string so that 'smith, john' matches a single person field containing both
    words, rather than allowing 'smith' and 'john' to match different people.
    """
    raw_parts = [p.strip() for p in segment.split(',') if p.strip()]
    name_parts = []
    date_parts = []
    for part in raw_parts:
        # Detect a year range pattern like "1630-1679"
        m = re.match(r'^(\d{4})\s*-\s*(\d{4})$', part)
        if m:
            date_parts.append(m.group(1))
            date_parts.append(m.group(2))
        elif re.match(r'^\d{4}$', part):
            # Single year like "1630"
            date_parts.append(part)
        else:
            name_parts.append(part)

    parts = []
    if name_parts:
        # Keep name parts as a single string so they match the same field
        parts.append(', '.join(name_parts))
    parts.extend(date_parts)
    return parts


def lookup_person_searchable(lookup_fn, field_name: str, value: str, rel_types: List[str]) -> Q:
    if not isinstance(value, str):
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    segments = [seg.strip() for seg in value.split('%') if seg.strip()]
    if not segments:
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    from person.models import CofkUnionPerson
    from work.models import CofkWorkPersonMap
    from django.db.models import Exists, OuterRef

    person_fields = [
        'person__foaf_name',
        'person__skos_altlabel',
        'person__person_aliases',
    ]

    negate = _is_negated_lookup(lookup_fn)

    pre_filter_q = Q()
    for segment in segments:
        parts = _parse_person_search_parts(segment)

        # Each part must match the SAME person record
        person_q = Q()
        for part in parts:
            part_q = Q()
            for field in person_fields:
                part_q |= Q(**{f'{field}__icontains': part})

            # Check year detail (constructed in StringAgg)
            # Year detail is: b. {birth} | d. {death} | {birth}-{death}
            # We can approximate this by checking birth and death years directly
            part_q |= Q(person__date_of_birth_year__icontains=part)
            part_q |= Q(person__date_of_death_year__icontains=part)

            person_q &= part_q

        exists_q = Exists(CofkWorkPersonMap.objects.filter(
            person_q,
            work_id=OuterRef('pk'),
            relationship_type__in=rel_types
        ))
        if negate:
            pre_filter_q &= ~exists_q
        else:
            pre_filter_q &= exists_q

    return pre_filter_q


def lookup_location_searchable(lookup_fn, field_name: str, value: str, rel_types: List[str]) -> Q:
    if not isinstance(value, str):
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    segments = [seg.strip() for seg in value.split('%') if seg.strip()]
    if not segments:
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    from location.models import CofkUnionLocation
    from work.models import CofkWorkLocationMap
    from django.db.models import Exists, OuterRef

    location_fields = [
        'location__location_name',
        'location__location_synonyms',
    ]

    negate = _is_negated_lookup(lookup_fn)

    pre_filter_q = Q()
    for segment in segments:
        loc_q = Q()
        for field in location_fields:
            loc_q |= Q(**{f'{field}__icontains': segment})

        exists_q = Exists(CofkWorkLocationMap.objects.filter(
            loc_q,
            work_id=OuterRef('pk'),
            relationship_type__in=rel_types
        ))
        if negate:
            pre_filter_q &= ~exists_q
        else:
            pre_filter_q &= exists_q

    return pre_filter_q


def lookup_related_resources(lookup_fn, field_name: str, value: str) -> Q:
    """
    Search the 'Related resources' column which displays both actual resources
    (via CofkWorkResourceMap) and related works such as 'Reply to', 'Answered by',
    and 'Matching letter' (via CofkWorkWorkMap).

    This function combines searches across both resource names and related work
    descriptions so that e.g. searching for 'match' finds works with a
    'Matching letter' relationship.
    """
    from core.constant import REL_TYPE_IS_RELATED_TO, REL_TYPE_WORK_IS_REPLY_TO, REL_TYPE_WORK_MATCHES
    from work.models import CofkWorkResourceMap, CofkWorkWorkMap
    from django.db.models import Exists, OuterRef

    if not isinstance(value, str):
        return query_serv.run_lookup_fn(lookup_fn, field_name, value)

    negate = _is_negated_lookup(lookup_fn)
    lookup_key = query_serv.get_lookup_key_by_lookup_fn(lookup_fn)

    # For is_blank / not_blank, check whether ANY related resource or related work exists
    if lookup_key in ('is_blank', 'not_blank'):
        resource_exists = Exists(CofkWorkResourceMap.objects.filter(
            work_id=OuterRef('pk'),
            relationship_type=REL_TYPE_IS_RELATED_TO,
        ))
        work_rel_types = [REL_TYPE_WORK_IS_REPLY_TO, REL_TYPE_WORK_MATCHES]
        work_from_exists = Exists(CofkWorkWorkMap.objects.filter(
            work_from_id=OuterRef('pk'),
            relationship_type__in=work_rel_types,
        ))
        work_to_exists = Exists(CofkWorkWorkMap.objects.filter(
            work_to_id=OuterRef('pk'),
            relationship_type__in=work_rel_types,
        ))
        any_exists = resource_exists | work_from_exists | work_to_exists
        if lookup_key == 'is_blank':
            return ~Q(any_exists)
        else:
            return Q(any_exists)

    # For text-based lookups, search resource_name and related work descriptions
    # Resources: search resource_name via CofkWorkResourceMap
    resource_q = Exists(CofkWorkResourceMap.objects.filter(
        work_id=OuterRef('pk'),
        relationship_type=REL_TYPE_IS_RELATED_TO,
        resource__resource_name__icontains=value,
    ))

    # Related works: the column displays labels like "Reply to: ...",
    # "Answered by: ...", "Matching letter: ..." followed by the work
    # description.  Match the search term against both the
    # label text AND the related work's description
    _LABEL_REL_TYPES = {
        'reply to': REL_TYPE_WORK_IS_REPLY_TO,
        'answered by': REL_TYPE_WORK_IS_REPLY_TO,
        'matching letter': REL_TYPE_WORK_MATCHES,
    }

    work_rel_types = [REL_TYPE_WORK_IS_REPLY_TO, REL_TYPE_WORK_MATCHES]

    # Check if the search value matches any of the display labels.
    # If so, include ALL works that have that relationship type.
    label_matched_types = set()
    val_lower = value.lower().strip()
    for label, rel_type in _LABEL_REL_TYPES.items():
        if val_lower in label or label in val_lower:
            label_matched_types.add((label, rel_type))

    combined = resource_q

    if label_matched_types:
        # The search term matches a label — return works that have the
        # corresponding relationship type in either direction.
        for label, rel_type in label_matched_types:
            if label == 'answered by':
                # "Answered by" shows in work_to_set (this work is the target)
                combined = combined | Exists(CofkWorkWorkMap.objects.filter(
                    work_to_id=OuterRef('pk'),
                    relationship_type=rel_type,
                ))
            elif label == 'reply to':
                # "Reply to" shows in work_from_set (this work is the source)
                combined = combined | Exists(CofkWorkWorkMap.objects.filter(
                    work_from_id=OuterRef('pk'),
                    relationship_type=rel_type,
                ))
            else:
                # "Matching letter" is bidirectional
                combined = combined | Exists(CofkWorkWorkMap.objects.filter(
                    work_from_id=OuterRef('pk'),
                    relationship_type=rel_type,
                )) | Exists(CofkWorkWorkMap.objects.filter(
                    work_to_id=OuterRef('pk'),
                    relationship_type=rel_type,
                ))

    # Also search the related work's description text (both directions)
    work_from_q = Exists(CofkWorkWorkMap.objects.filter(
        work_from_id=OuterRef('pk'),
        relationship_type__in=work_rel_types,
        work_to__description__icontains=value,
    ))
    work_to_q = Exists(CofkWorkWorkMap.objects.filter(
        work_to_id=OuterRef('pk'),
        relationship_type__in=work_rel_types,
        work_from__description__icontains=value,
    ))

    combined = combined | work_from_q | work_to_q
    if negate:
        return ~Q(combined)
    return Q(combined)
