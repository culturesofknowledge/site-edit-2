import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

link_pattern = re.compile(r'(xxxCofkLinkStartxxx)(xxxCofkHrefStartxxx)(.*?)(xxxCofkHrefEndxxx)(.*?)(xxxCofkLinkEndxxx)')


@register.filter
def render_queryable_manif(values: str):
    return mark_safe(re.sub(link_pattern, r'<a href="\3">\5</a>', values))
