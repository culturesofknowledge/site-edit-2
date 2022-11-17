import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')


@register.filter
def render_queryable_resources(values: str):
    html = '<ul>'
    for link in re.findall(link_pattern, values):
        html += f'<li><a href="{link[2]}">{link[4]}</a></li>'
    html += '</ul>'

    return mark_safe(html)
