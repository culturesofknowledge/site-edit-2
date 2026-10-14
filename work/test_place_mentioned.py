from types import SimpleNamespace

from django.test import TestCase

from core.constant import REL_TYPE_MENTION_PLACE
from core.forms import PlaceMentionedRecrefForm
from core.helper import test_serv
from core.helper.recref_handler import MultiRecrefAdapterHandler
from work.models import CofkWorkLocationMap
from work.recref_adapter import WorkLocRecrefAdapter


class PlaceMentionedIssuesTests(TestCase):
    """
    'Issues with place mentioned' checkboxes are stored on each work-location
    recref record instead of the work record, so every place mentioned has
    its own inferred / uncertain flags.
    """

    def setUp(self):
        test_serv.create_empty_lookup_cat()
        self.work = test_serv.create_work_by_dict()
        self.location = test_serv.create_location_by_dict()
        self.request = SimpleNamespace(user=SimpleNamespace(username='tester'))

    def create_handler(self, request_data):
        return MultiRecrefAdapterHandler(
            request_data, name='place',
            recref_adapter=WorkLocRecrefAdapter(self.work),
            recref_form_class=PlaceMentionedRecrefForm,
            rel_type=REL_TYPE_MENTION_PLACE,
        )

    def find_recref(self) -> CofkWorkLocationMap:
        return CofkWorkLocationMap.objects.get(work=self.work,
                                               relationship_type=REL_TYPE_MENTION_PLACE)

    def test_create_with_issues(self):
        self.create_handler({
            'new_place-target_id': self.location.pk,
            'new_place-place_mentioned_inferred': 'on',
            'new_place-place_mentioned_uncertain': 'on',
            'recref_place-TOTAL_FORMS': '0',
            'recref_place-INITIAL_FORMS': '0',
        }).maintain_record(self.request, self.work)

        recref = self.find_recref()
        self.assertEqual(recref.place_mentioned_inferred, 1)
        self.assertEqual(recref.place_mentioned_uncertain, 1)

    def test_update_issues(self):
        recref = CofkWorkLocationMap(work=self.work, location=self.location,
                                     relationship_type=REL_TYPE_MENTION_PLACE,
                                     place_mentioned_inferred=1,
                                     place_mentioned_uncertain=1)
        recref.update_current_user_timestamp('tester')
        recref.save()

        # inferred unticked, uncertain stays ticked
        self.create_handler({
            'new_place-target_id': '',
            'recref_place-TOTAL_FORMS': '1',
            'recref_place-INITIAL_FORMS': '1',
            'recref_place-0-recref_id': recref.pk,
            'recref_place-0-target_id': self.location.pk,
            'recref_place-0-place_mentioned_uncertain': 'on',
        }).maintain_record(self.request, self.work)

        recref = self.find_recref()
        self.assertEqual(recref.place_mentioned_inferred, 0)
        self.assertEqual(recref.place_mentioned_uncertain, 1)
