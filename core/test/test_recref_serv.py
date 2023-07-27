from django.test import TestCase

import location.fixtures
import location.fixtures
from location.models import CofkLocationCommentMap
from location.recref_adapter import LocationCommentRecrefAdapter
from siteedit2.serv import test_serv


class RecrefUtilsTests(TestCase):

    def test_find_recref_list(self):
        loc_a = location.fixtures.create_location_a()
        loc_a.save()

        comment_msg_list = ['aaaaa', 'bbbb', 'ccc']
        test_serv.add_comments_by_msgs(comment_msg_list, loc_a, LocationCommentRecrefAdapter)
        self.assertEqual(test_serv.cnt_recref(CofkLocationCommentMap, loc_a), len(comment_msg_list))
