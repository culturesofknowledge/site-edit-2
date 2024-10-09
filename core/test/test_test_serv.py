from django.test import TestCase

from core.helper import test_serv, recref_serv
from core.models import CofkUnionComment
from location.models import CofkUnionLocation


class TestServTests(TestCase):

    def test_add_comments_by_msgs(self):
        location = CofkUnionLocation(pk=1)
        location.save()
        msgs = ['aaaaa', 'bbbb', 'ccc']
        recref_list = test_serv.add_comments_by_msgs(msgs, location)
        n_org_comments = CofkUnionComment.objects.count()

        assert set(recref_list) == set(recref_serv.find_all_recref_by_models([location]))
        assert set(msgs) == {recref.comment.comment for recref in recref_list}
        assert n_org_comments == CofkUnionComment.objects.count()
