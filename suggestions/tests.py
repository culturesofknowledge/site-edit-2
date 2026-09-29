from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from core import constant
from core.helper import perm_serv
from login.fixtures import create_test_user
from suggestions.models import CofkSuggestions


def create_suggestions_user(username, role=None):
    user = create_test_user(username)
    for perm in [constant.PM_VIEW_SUGGESTIONS, constant.PM_CHANGE_SUGGESTIONS]:
        user.user_permissions.add(perm_serv.get_perm_by_full_name(perm))
    if role:
        user.groups.add(Group.objects.get_or_create(name=role)[0])
    return user


class SuggestionFilterTests(TestCase):
    """ emlo-project#831 """

    def setUp(self):
        self.contributor = create_suggestions_user('contributor@example.org')
        self.editor = create_suggestions_user('editor@example.org', role=constant.ROLE_EDITOR)

        def create(suggestion_type, new, author):
            return CofkSuggestions.objects.create(suggestion_type=suggestion_type, suggestion_new=new,
                                                  suggestion_suggestion='x', suggestion_author=author)

        self.new_person = create('Person', True, self.contributor)
        self.existing_person = create('Person', False, self.contributor)
        self.new_location = create('Location', True, self.contributor)
        self.editors_publication = create('Publication', True, self.editor)

    def get_ids(self, user, **params):
        self.client.force_login(user)
        response = self.client.get(reverse('suggestions:suggestion_all'), params)
        self.assertEqual(response.status_code, 200)
        return {s.pk for s in response.context['query_results']}

    def test_editor_no_filter_shows_all(self):
        self.assertEqual(self.get_ids(self.editor),
                         {self.new_person.pk, self.existing_person.pk, self.new_location.pk,
                          self.editors_publication.pk})

    def test_editor_filter_by_type(self):
        self.assertEqual(self.get_ids(self.editor, person='on'), {self.new_person.pk, self.existing_person.pk})
        self.assertEqual(self.get_ids(self.editor, person='on', location='on'),
                         {self.new_person.pk, self.existing_person.pk, self.new_location.pk})

    def test_editor_filter_by_new_or_existing(self):
        self.assertEqual(self.get_ids(self.editor, showExisting='on'), {self.existing_person.pk})
        self.assertEqual(self.get_ids(self.editor, person='on', showNew='on'), {self.new_person.pk})

    def test_contributor_only_sees_own(self):
        self.assertEqual(self.get_ids(self.contributor),
                         {self.new_person.pk, self.existing_person.pk, self.new_location.pk})
        self.assertEqual(self.get_ids(self.contributor, publication='on'), set())
        self.assertEqual(self.get_ids(self.contributor, person='on', showNew='on'), {self.new_person.pk})
