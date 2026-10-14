from types import SimpleNamespace

from django.contrib.messages.storage.fallback import FallbackStorage
from django.template import Context, Template
from django.test import TestCase, RequestFactory

from core.helper import data_serv
from core.templatetags.cl_filters import render_display_link
from person.fixtures import create_person_obj
from work.templatetags.work_util_tags import display_resources, render_queryable_manif, \
    render_queryable_images, more_info, exclamation
from work.models import CofkUnionWork
from work.work_serv import DisplayableWork

PAYLOAD = '<script>alert(1)</script>'
ESCAPED_PAYLOAD = '&lt;script&gt;alert(1)&lt;/script&gt;'
JS_URL = 'javascript:alert(1)'


def encoded_link(url, text):
    return data_serv.endcode_url_content(url, text)


class TestSafeUrl(TestCase):

    def test_allowed(self):
        for url in ['https://example.org/a?b=1&c=2', 'http://example.org', '/work/1', 'page.html',
                    'mailto:a@example.org', '']:
            self.assertTrue(data_serv.is_safe_url(url), url)

    def test_rejected(self):
        for url in [JS_URL, 'JavaScript:alert(1)', ' javascript:alert(1)', 'java\tscript:alert(1)',
                    '\x01javascript:alert(1)', 'data:text/html,<script>', 'vbscript:x']:
            self.assertFalse(data_serv.is_safe_url(url), url)

    def test_render_link(self):
        self.assertEqual(data_serv.render_link('https://example.org/?a=1&b=2', PAYLOAD),
                         f'<a href="https://example.org/?a=1&amp;b=2" target="_blank">{ESCAPED_PAYLOAD}</a>')
        self.assertEqual(data_serv.render_link(JS_URL, 'text'), 'text')


class TestWorkUtilTags(TestCase):

    def test_display_resources_escapes(self):
        result = display_resources(f'{PAYLOAD} | {encoded_link("https://example.org", PAYLOAD)}')

        self.assertNotIn('<script>', result)
        self.assertIn(ESCAPED_PAYLOAD, result)
        self.assertIn('href="https://example.org"', result)

    def test_display_resources_drops_javascript_url(self):
        result = display_resources(encoded_link(JS_URL, 'click'))

        self.assertNotIn('javascript:', result)
        self.assertIn('click', result)

    def test_render_queryable_manif_escapes(self):
        result = render_queryable_manif(f'{PAYLOAD}\n{encoded_link(JS_URL, PAYLOAD)}'
                                        f'{encoded_link("https://example.org", "ok")}')

        self.assertNotIn('<script>', result)
        self.assertNotIn('javascript:', result)
        self.assertIn('<br>', result)
        self.assertIn('<a href="https://example.org" target="_blank">ok</a>', result)

    def test_render_queryable_images(self):
        values = ('xxxCofkImageIDStartxxx"><script>xxxCofkImageIDEndxxx, '
                  f'xxxCofkImageIDStartxxx{JS_URL}xxxCofkImageIDEndxxx, '
                  'xxxCofkImageIDStartxxxhttps://example.org/a.jpgxxxCofkImageIDEndxxx')
        result = render_queryable_images(values)

        self.assertNotIn('<script>', result)
        self.assertNotIn('javascript:', result)
        self.assertIn('src="https://example.org/a.jpg"', result)

    def test_tooltips_are_escaped_for_tippy(self):
        # tippy renders data-tippy-content as HTML, so after the template's attribute
        # escaping has been undone by the browser, the payload must still be escaped
        work = SimpleNamespace(notes_on_authors='', creators_searchable='', addressees_searchable='',
                               subjects_for_display='', abstract=PAYLOAD, general_notes='')
        flagged_work = CofkUnionWork(date_of_work_inferred=1, date_of_work_as_marked=PAYLOAD)

        self.assertIn(ESCAPED_PAYLOAD, more_info(work))
        self.assertIn(ESCAPED_PAYLOAD, exclamation(flagged_work))

    def test_other_details_escapes(self):
        work = DisplayableWork(keywords=PAYLOAD, abstract=PAYLOAD, work_id='w1', iwork_id=1)
        work.save()

        result = work.other_details

        self.assertNotIn('<script>', result)
        self.assertIn(f'<strong>Keywords</strong>: {ESCAPED_PAYLOAD}', result)


class TestPersonAndFilters(TestCase):

    def test_names_and_roles_escapes(self):
        person = create_person_obj()
        person.foaf_name = PAYLOAD
        person.save()

        self.assertEqual(person.names_and_roles, f'<p>{ESCAPED_PAYLOAD}</p>')

    def test_render_display_link(self):
        result = render_display_link(f'{PAYLOAD} __@_[{JS_URL}]x_@__ __@_[https://e.org/?a=1&b=2]{PAYLOAD}_@__')

        self.assertNotIn('<script>', result)
        self.assertNotIn('javascript:', result)
        self.assertIn(f'<a href="https://e.org/?a=1&amp;b=2" target="_blank">{ESCAPED_PAYLOAD}</a>', result)

    def test_messages_are_escaped(self):
        request = RequestFactory().get('/')
        request.session = {}
        storage = FallbackStorage(request)
        storage.add(20, f'Successfully deleted catalogue "{PAYLOAD}"')

        rendered = Template('{% include "core/component/messages.html" %}').render(
            Context({'messages': storage}))

        self.assertNotIn('<script>', rendered)
        self.assertIn(ESCAPED_PAYLOAD, rendered)
