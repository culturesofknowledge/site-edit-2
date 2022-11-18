import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')


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
