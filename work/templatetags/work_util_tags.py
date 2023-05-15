import re

from django import template
from django.utils.safestring import mark_safe

from work import work_utils
from work.models import CofkUnionQueryableWork, CofkUnionWork

register = template.Library()

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')
img_pattern = re.compile(r'(xxxCofkImageIDStartxxx)(.*?)(xxxCofkImageIDEndxxx)')


@register.filter
def exclamation(work: CofkUnionWork):
    return work_utils.flags(work)


@register.filter
def more_info(work: CofkUnionWork):
    # KTODO convert to CofkUnionWork
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
            html += f'<li><a href="{link[2]}" target="_blank">{link[4]}</a></li>'
        html += '</ul>'
    elif len(resources) == 1:
        html = f'<a href="{resources[0][2]}" target="_blank">{resources[0][4]}</a>'

    return mark_safe(html)


@register.filter
def render_queryable_manif(values: str):
    return mark_safe(re.sub(link_pattern, r'<a href="\3" target="_blank">\5</a>', values))


@register.filter
def render_queryable_images(values: str):
    html = ''
    for img in re.findall(img_pattern, values):
        html += f'<a href="{img[1]}" target="_blank"><img src="{img[1]}" class="search_result_img"></a>'

    return mark_safe(html)
