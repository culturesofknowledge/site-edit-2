from django.test import TestCase

import location.fixtures
import location.fixtures
from location.models import CofkLocationCommentMap
from location.recref_adapter import LocationCommentRecrefAdapter
from siteedit2.utils import test_utils


class RecrefUtilsTests(TestCase):

    def test_find_recref_list(self):
        loc_a = location.fixtures.create_location_a()
        loc_a.save()

        comment_msg_list = ['aaaaa', 'bbbb', 'ccc']
        test_utils.add_comments_by_msgs(comment_msg_list, loc_a, LocationCommentRecrefAdapter)
        self.assertEqual(test_utils.cnt_recref(CofkLocationCommentMap, loc_a), len(comment_msg_list))
