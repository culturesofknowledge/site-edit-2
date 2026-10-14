import html
import re

from django import template
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from core.helper import data_serv
from core.helper.data_serv import link_pattern
from core import constant
from work import work_serv
from work.models import CofkUnionWork
from work.work_serv import DisplayableWork

register = template.Library()

img_pattern = re.compile(r'(xxxCofkImageIDStartxxx)(.*?)(xxxCofkImageIDEndxxx)')


# The two filters below feed data-tippy-content attributes, and tippy is set up with
# allowHTML (see emlo_base.html), so the attribute value is parsed as HTML. Escape the
# record data here, on top of the template's attribute escaping, so it shows as text.

@register.filter
def exclamation(work: CofkUnionWork):
    return html.escape(work_serv.flags(work))


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

    return html.escape(', '.join(tooltip))


@register.filter
def display_resources(values: str) -> str:
    """Render encoded link content as HTML list items.

    Supports plain-text labels (e.g. "Reply to:") that appear between
    encoded link markers — they are rendered as bold list items so that
    relationship types are visible in search results.
    """
    if not values:
        return ''

    # Split on the full encoded-link pattern, keeping separators
    segments = re.split(r'(xxxCofkLinkStartxxx.*?xxxCofkLinkEndxxx)', values)
    html_str = '<ul>'
    has_content = False
    for segment in segments:
        m = re.match(link_pattern, segment)
        if m:
            link, text = m.group(3), m.group(5)
            html_str += format_html('<li>{}</li>', data_serv.render_link(link, text))
            has_content = True
        else:
            # Plain text between links — may contain labels like "Reply to:"
            for piece in re.split(r'\s*\|\s*', segment):
                piece = piece.strip(' ,')
                if piece:
                    html_str += format_html('<li style="list-style:none;"><strong>{}</strong></li>', piece)
                    has_content = True
    html_str += '</ul>'

    return mark_safe(html_str) if has_content else ''


@register.filter
def render_queryable_manif(values: str):
    result = ''
    last_end = 0
    for m in re.finditer(link_pattern, values):
        result += conditional_escape(values[last_end:m.start()])
        result += data_serv.render_link(m.group(3), m.group(5))
        last_end = m.end()
    result += conditional_escape(values[last_end:])
    result = result.replace('\n', '<br>')
    return mark_safe(result)


@register.filter
def render_queryable_images(values: str):
    html_str = ''
    for img in re.findall(img_pattern, values):
        if data_serv.is_safe_url(img[1]):
            html_str += format_html('<a href="{0}" target="_blank"><img src="{0}" class="search_result_img"></a>',
                                    img[1])

    return mark_safe(html_str)

@register.filter
def format_group_name(group_name):
    """Convert group name to display name"""
    for role, display_name in constant.ROLE_DISPLAY_NAMES:
        if group_name == role:
            return display_name
    return group_name

