from django import template

register = template.Library()


@register.filter
def reverse_list(values):
    return reversed(values)


@register.filter
def is_general_true(value):
    return value in (1, '1', True, 'Y', 'y',)
