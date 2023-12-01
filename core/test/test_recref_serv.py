from django.test import TestCase

import location.fixtures
import location.fixtures
from core.helper import recref_serv
from core.models import CofkUnionComment
from location.models import CofkLocationCommentMap
from location.recref_adapter import LocationCommentRecrefAdapter
from manifestation.models import CofkManifCommentMap, CofkUnionManifestation
from siteedit2.serv import test_serv


class RecrefUtilsTests(TestCase):

    def test_find_recref_list(self):
        loc_a = location.fixtures.create_location_a()
        loc_a.save()

        comment_msg_list = ['aaaaa', 'bbbb', 'ccc']
        test_serv.add_comments_by_msgs(comment_msg_list, loc_a, LocationCommentRecrefAdapter)
        self.assertEqual(test_serv.cnt_recref(CofkLocationCommentMap, loc_a), len(comment_msg_list))


    def test_get_left_right_rel_obj(self):
        comment = CofkUnionComment()
        comment.save()

        manif = CofkUnionManifestation()
        manif.save()

        recref = CofkManifCommentMap()
        recref.relationship_type = 'refers_to'
        recref.comment = comment
        recref.manifestation = manif

        left_obj, right_obj = recref_serv.get_left_right_rel_obj(recref)
        assert left_obj == comment
        assert right_obj == manif
