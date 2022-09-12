from django import template

register = template.Library()


@register.filter
def reverse_list(values):
    return reversed(values)
