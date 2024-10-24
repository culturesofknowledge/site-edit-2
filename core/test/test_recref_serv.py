from django.test import TestCase

import location.fixtures
import location.fixtures
from core.helper import recref_serv, test_serv
from core.models import CofkUnionComment
from location.models import CofkLocationCommentMap
from manifestation.models import CofkManifCommentMap, CofkUnionManifestation
from person.models import CofkUnionPerson
from work.models import CofkUnionWork, CofkWorkLocationMap
from work.recref_adapter import WorkPersonRecrefAdapter


class RecrefUtilsTests(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.rel_type_a = 'rel_type_a'

        cls.work = CofkUnionWork(pk=1)
        cls.work.save()

        cls.work2 = CofkUnionWork(pk=2)
        cls.work2.save()

        cls.persons = [CofkUnionPerson(foaf_name=f'person_{i}') for i in range(3)]
        cls.persons2 = [CofkUnionPerson(foaf_name=f'person2_{i}') for i in range(2)]

        recref_adapter = WorkPersonRecrefAdapter()
        for w, _persons in [(cls.work, cls.persons), (cls.work2, cls.persons2)]:
            for p in _persons:
                p.save()
                recref = recref_adapter.upsert_recref(
                    rel_type=cls.rel_type_a,
                    parent_instance=w,
                    target_instance=p,
                )
                recref.save()

    def test_find_recref_list(self):
        loc_a = location.fixtures.create_location_a()
        loc_a.save()

        comment_msg_list = ['aaaaa', 'bbbb', 'ccc']
        test_serv.add_comments_by_msgs(comment_msg_list, loc_a)
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

    def test_find_all_recref_by_models(self):
        recref_adapter = WorkPersonRecrefAdapter()

        recref_list = list(recref_serv.find_all_recref_by_models([self.work, self.work2]))

        assert len(recref_list) == (len(self.persons) + len(self.persons2))
        assert set(r.relationship_type for r in recref_list) == {self.rel_type_a}
        assert {r.person for r in recref_list} == (set(self.persons) | set(self.persons2))

    def test_get_parent_related_field_by_recref(self):
        recref_list = list(recref_serv.find_all_recref_by_models([self.work]))
        parent_field, related_field = recref_serv.get_parent_related_field_by_recref(recref_list[0], self.work)
        assert parent_field.field.name == 'work'
        assert related_field.field.name == 'person'

    def test_find_bounded_data_list_by_related_model(self):
        bounded_data_list = list(recref_serv.find_bounded_data_list_by_related_model(self.work))
        assert bounded_data_list

        target_recref_class = CofkWorkLocationMap
        target_bounded_data = None
        for bounded_data in bounded_data_list:
            if bounded_data.recref_class == target_recref_class:
                target_bounded_data = bounded_data
                break

        assert target_bounded_data is not None

        assert target_bounded_data.recref_class
        assert CofkUnionWork in set(target_bounded_data.pair_related_models)

    def test_find_bounded_data_list_by_related_model__object_class_input(self):
        assert list(recref_serv.find_bounded_data_list_by_related_model(self.work)) == \
               list(recref_serv.find_bounded_data_list_by_related_model(CofkUnionWork))
