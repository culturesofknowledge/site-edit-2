import re

from django import template
from django.core.paginator import Page
from django.template.defaultfilters import date as date_filter
from django.utils.safestring import mark_safe
from django.utils.html import escape

from core.constant import ENTITIES

STANDARD_DATETIME_FORMAT = "d M Y H:i"

register = template.Library()


@register.filter
def standard_datetime(value):
    """Format a datetime using the project-wide standard format."""
    if not value:
        return ''
    return date_filter(value, STANDARD_DATETIME_FORMAT)


@register.filter
def reverse_list(values):
    return reversed(values)


@register.filter
def is_general_true(value):
    return value in (1, '1', True, 'Y', 'y',)


@register.filter
def get_elided_page_range(page: Page, on_each_side=2, on_ends=2):
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


@register.filter
def can_show_for_perm(perm, perms):
    return perm is None or perm in perms


@register.filter
def render_display_link(value):
    value = re.sub(r'__@_\[(.+?)\](.+?)_@__', r'<a href="\1" target="_blank">\2</a>', value)
    return mark_safe(value)


@register.filter
def bulleted(value):
    """Render a string (or list/tuple) as an HTML bullet-pointed list.

    - If value is a string, it will be split on newlines and semicolons.
    - Empty items are ignored.
    - Output is marked safe as it is escaped per item.
    """
    if not value:
        return ''

    if isinstance(value, (list, tuple)):
        items = [str(v) for v in value]
    else:
        items = re.split(r'[;\r\n]+', str(value))

    items = [i.strip() for i in items if i and i.strip()]
    if not items:
        return ''

    lis = ''.join(f'<li>{escape(i)}</li>' for i in items)
    return mark_safe(f'<ul class="bullet-list">{lis}</ul>')


@register.filter
def break_ambiguous(value):
    """
    Inserts a <wbr> tag after '/', ',', '.', '=' and '&' characters to
    provide potential break points for long URLs or strings in narrow columns.
    """
    if not isinstance(value, str):
        return value

    # We escape first to be safe, then replace.
    # We use <wbr> (Word Break Opportunity) instead of Unicode zero-width space
    # \u200b because \u200b can be treated as an invalid character when
    # copying URLs or when browsers interpret them. <wbr> is purely visual.
    value = escape(str(value))
    for char in ['/', ',', '.', '=']:
        value = value.replace(char, char + '<wbr>')
    
    # We must replace '&amp;' which was produced by escape() 
    # if we want to allow breaks after ampersands in the original text.
    value = value.replace('&amp;', '&amp;<wbr>')
    
    return mark_safe(value)

@register.filter
def add_another_if_startswith(value, prefix="Add "):
    if not isinstance(value, str):
        return value

    if value.startswith(prefix):
        return value.replace(prefix, "Add another ", 1)

    return value
