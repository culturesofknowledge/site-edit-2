import re

from django import template
from django.utils.safestring import mark_safe

from work.models import CofkUnionQueryableWork

register = template.Library()

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')
img_pattern = re.compile(r'(xxxCofkImageIDStartxxx)(.*?)(xxxCofkImageIDEndxxx)')


@register.filter
def exclamation(work: CofkUnionQueryableWork):
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


@register.filter
def more_info(work: CofkUnionQueryableWork):
    tooltip = []

    if work.notes_on_authors:
        tooltip.append(f'Role of author/sender: {work.notes_on_authors}\n')

    if work.creators_searchable.find('alias:') > -1:
        tooltip.append(f'Further details of author: {work.creators_searchable}')

    if work.addressees_searchable.find('alias:') > -1:
        tooltip.append(f'Further details of addressee: {work.addressees_searchable}')

    if work.subjects:
        tooltip.append(f'Subject(s): {work.subjects}\n')

    if work.abstract:
        tooltip.append(f'{work.abstract}\n')

    if work.general_notes:
        tooltip.append(f'Notes: {work.general_notes}\n')

    return ', '.join(tooltip)


@register.filter
def render_queryable_resources(values: str):
    resources = re.findall(link_pattern, values)
    html = values

    if len(resources) > 1:
        html = '<ul>'
        for link in resources:
            html += f'<li><a href="{link[2]}">{link[4]}</a></li>'
        html += '</ul>'
    elif len(resources) == 1:
        html = f'<a href="{resources[0][2]}">{resources[0][4]}</a>'

    return mark_safe(html)


@register.filter
def render_queryable_manif(values: str):
    return mark_safe(re.sub(link_pattern, r'<a href="\3">\5</a>', values))


@register.filter
def render_queryable_images(values: str):
    html = ''
    for img in re.findall(img_pattern, values):
        html += f'<a href="{img[1]}" target="_blank"><img src="{img[1]}" class="search_result_img"></a>'

    return mark_safe(html)


@register.filter
def other_details(work: CofkUnionQueryableWork):
    _other_details = []

    if work.abstract:
        _other_details.append(f'<strong>Abstract</strong>: {work.abstract}')

    if work.language_of_work:
        if len(work.language_of_work.split(',')) > 1:
            _other_details.append(f'<strong>Languages</strong>: {work.language_of_work}')
        else:
            _other_details.append(f'<strong>Language</strong>: {work.language_of_work}')

    if work.general_notes:
        _other_details.append(f'<strong>Notes</strong>: {work.general_notes}')

    if work.people_mentioned:
        _other_details.append(f'<strong>People mentioned</strong>: {work.people_mentioned}')

    return mark_safe('<br/><br/>'.join(_other_details))

@register.filter
def date_for_ordering(work: CofkUnionQueryableWork):
    date = []

    if work.date_of_work_std_year:
        date.append(str(work.date_of_work_std_year))

    if work.date_of_work_std_month:
        date.append(str(work.date_of_work_std_month))

    if work.date_of_work_std_day:
        date.append(str(work.date_of_work_std_day))

    return '-'.join(date)
