from types import SimpleNamespace

from django.test import TestCase

from core.constant import REL_TYPE_MENTION
from core.forms import PersonMentionedRecrefForm
from core.helper import test_serv
from core.helper.recref_handler import MultiRecrefAdapterHandler
from work.models import CofkWorkPersonMap
from work.recref_adapter import WorkPersonRecrefAdapter


class PersonMentionedIssuesTests(TestCase):
    """
    'Issues with person mentioned' checkboxes are stored on each work-person
    recref record instead of the work record, so every person mentioned has
    its own inferred / uncertain flags.
    """

    def setUp(self):
        test_serv.create_empty_lookup_cat()
        self.work = test_serv.create_work_by_dict()
        self.person = test_serv.create_person_by_dict()
        self.request = SimpleNamespace(user=SimpleNamespace(username='tester'))

    def create_handler(self, request_data):
        return MultiRecrefAdapterHandler(
            request_data, name='people',
            recref_adapter=WorkPersonRecrefAdapter(self.work),
            recref_form_class=PersonMentionedRecrefForm,
            rel_type=REL_TYPE_MENTION,
        )

    def find_recref(self) -> CofkWorkPersonMap:
        return CofkWorkPersonMap.objects.get(work=self.work,
                                             relationship_type=REL_TYPE_MENTION)

    def test_create_with_issues(self):
        self.create_handler({
            'new_people-target_id': self.person.pk,
            'new_people-person_mentioned_inferred': 'on',
            'new_people-person_mentioned_uncertain': 'on',
            'recref_people-TOTAL_FORMS': '0',
            'recref_people-INITIAL_FORMS': '0',
        }).maintain_record(self.request, self.work)

        recref = self.find_recref()
        self.assertEqual(recref.person_mentioned_inferred, 1)
        self.assertEqual(recref.person_mentioned_uncertain, 1)

    def test_update_issues(self):
        recref = CofkWorkPersonMap(work=self.work, person=self.person,
                                   relationship_type=REL_TYPE_MENTION,
                                   person_mentioned_inferred=1,
                                   person_mentioned_uncertain=1)
        recref.update_current_user_timestamp('tester')
        recref.save()

        # inferred unticked, uncertain stays ticked
        self.create_handler({
            'new_people-target_id': '',
            'recref_people-TOTAL_FORMS': '1',
            'recref_people-INITIAL_FORMS': '1',
            'recref_people-0-recref_id': recref.pk,
            'recref_people-0-target_id': self.person.pk,
            'recref_people-0-person_mentioned_uncertain': 'on',
        }).maintain_record(self.request, self.work)

        recref = self.find_recref()
        self.assertEqual(recref.person_mentioned_inferred, 0)
        self.assertEqual(recref.person_mentioned_uncertain, 1)
