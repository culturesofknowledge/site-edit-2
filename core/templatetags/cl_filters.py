from django import template
from django.core.paginator import Page

register = template.Library()


@register.filter
def reverse_list(values):
    return reversed(values)


@register.filter
def is_general_true(value):
    return value in (1, '1', True, 'Y', 'y',)


@register.filter
def get_elided_page_range(page: Page, on_each_side=3, on_ends=2):
    return page.paginator.get_elided_page_range(number=page.number, on_each_side=on_each_side, on_ends=on_ends)
