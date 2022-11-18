import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

img_pattern = re.compile(r'(xxxCofkImageIDStartxxx)(.*?)(xxxCofkImageIDEndxxx)')


@register.filter
def render_queryable_images(values: str):
    html = ''
    for img in re.findall(img_pattern, values):
        html += f'<a href="{img[1]}"><img src="{img[1]}" class="search_result_img"></a>'

    return mark_safe(html)
