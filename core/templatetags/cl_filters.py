from django import template
from django.core.paginator import Page

from core.constant import ENTITIES

register = template.Library()


@register.filter
def reverse_list(values):
    return reversed(values)


@register.filter
def is_general_true(value):
    return value in (1, '1', True, 'Y', 'y',)


@register.filter
def get_elided_page_range(page: Page, on_each_side=8, on_ends=4):
    return page.paginator.get_elided_page_range(number=page.number, on_each_side=on_each_side, on_ends=on_ends)


@register.filter
def get_results_on_page(page: Page) -> str:
    start = (1 + (page.number - 1) * page.paginator.per_page)
    end = min(page.paginator.per_page * page.number, page.paginator.count)
    return f'{start:,}–{end:,}'


@register.filter
def get_entity(_class: str) -> str:
    if _class in ENTITIES:
        return ENTITIES[_class].title()
    return _class.title()


@register.filter
def add_classes(value, arg):
    """
    Add provided classes to form field
    :param value: form field
    :param arg: string of classes separated by ' '
    :return: edited field
    """
    css_classes = value.field.widget.attrs.get('class', '').strip()
    # check if class is set or empty and split its content to list (or init list)
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []

    # prepare new classes to list
    class_names = arg.strip().split(' ')
    class_names = (c.strip() for c in class_names)
    class_names = filter(None, class_names)
    css_classes = set(
        css_classes + list(class_names)
    )

    # join back to single string
    return value.as_widget(attrs={'class': ' '.join(css_classes)})


@register.simple_tag
def url_replace(request, field, value):
    d = request.GET.copy()
    d[field] = value
    return d.urlencode()
