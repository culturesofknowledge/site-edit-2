import re

from django import template
from django.utils.safestring import mark_safe

from core.helper import data_serv
from core.helper.data_serv import link_pattern
from work import work_serv
from work.models import CofkUnionWork
from work.work_serv import DisplayableWork

register = template.Library()

img_pattern = re.compile(r'(xxxCofkImageIDStartxxx)(.*?)(xxxCofkImageIDEndxxx)')


@register.filter
def exclamation(work: CofkUnionWork):
    return work_serv.flags(work)


@register.filter
def more_info(work: DisplayableWork):
    tooltip = []

    if work.notes_on_authors:
        tooltip.append(f'Role of author/sender: {work.notes_on_authors}\n')

    if work.creators_searchable.find('alias:') > -1:
        tooltip.append(f'Further details of author: {work.creators_searchable}')

    if work.addressees_searchable.find('alias:') > -1:
        tooltip.append(f'Further details of addressee: {work.addressees_searchable}')

    if work.subjects_for_display:
        tooltip.append(f'Subject(s): {work.subjects_for_display}\n')

    if work.abstract:
        tooltip.append(f'{work.abstract}\n')

    if work.general_notes:
        tooltip.append(f'Notes: {work.general_notes}\n')

    return ', '.join(tooltip)


@register.filter
def display_resources(values: str):
    resources = list(data_serv.decode_multi_url_content(values))

    html = ''
    if len(resources) > 1:
        html = '<ul>'
        for link, text in resources:
            html += f'<li><a href="{link}" target="_blank">{text}</a></li>'
        html += '</ul>'
    elif len(resources) == 1:
        html = f'<a href="{resources[0][0]}" target="_blank">{resources[0][1]}</a>'

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
