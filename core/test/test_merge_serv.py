from django.test import TestCase

from core.helper import merge_serv, test_serv
from core.models import MergeHistory
from location.models import CofkUnionLocation


class MergeServTests(TestCase):

    def test_merge(self):
        locations = []
        for key in range(1, 4):
            loc = CofkUnionLocation(pk=key)
            loc.save()
            locations.append(loc)

        merged_id = locations[2].pk

        assert locations[0].comments.count() == 0
        test_serv.add_comments_by_msgs(['aa', 'bb'], locations[1])
        test_serv.add_comments_by_msgs(['cc'], locations[2])

        merge_serv.merge(locations[0], [locations[1], locations[2]])
        assert locations[0].comments.count() == 3
        assert 'aa' in [c.comment for c in locations[0].comments.all()]
        assert MergeHistory.objects.count() == 2
        assert MergeHistory.objects.filter(new_id=locations[0].pk).count() == 2
        assert MergeHistory.objects.filter(old_id=merged_id).count() == 1
