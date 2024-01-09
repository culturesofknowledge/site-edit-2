from django.test import TestCase

from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation, CofkManifManifMap
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkWorkMap
from work.recref_adapter import WorkLocRecrefAdapter, EarlierLetterRecrefAdapter, LaterLetterRecrefAdapter, EnclosureManifRecrefAdapter, EnclosedManifRecrefAdapter
from django.test import TestCase

from location.models import CofkUnionLocation
from manifestation.models import CofkUnionManifestation, CofkManifManifMap
from work.models import CofkUnionWork, CofkWorkLocationMap, CofkWorkWorkMap
from work.recref_adapter import WorkLocRecrefAdapter, EarlierLetterRecrefAdapter, LaterLetterRecrefAdapter, \
    EnclosureManifRecrefAdapter, EnclosedManifRecrefAdapter


class RecrefFormAdapterTest(TestCase):

    def test_work_loc_recref_adapter(self):
        # prepare data
        rel_type = 'aaa'
        parent = CofkUnionWork()
        parent.save()

        target = CofkUnionLocation()
        target.save()

        recref_adapter = WorkLocRecrefAdapter(parent)
        recref_class = CofkWorkLocationMap

        self._test_recref_form_adapter(parent, target, rel_type, recref_adapter, recref_class)

    def test_earlier_letter_recref_adapter(self):
        # prepare data
        rel_type = 'aaa'
        parent = CofkUnionWork()
        parent.save()
        target = CofkUnionWork()
        target.save()
        recref_adapter = EarlierLetterRecrefAdapter(parent)
        recref_class = CofkWorkWorkMap
        self._test_recref_form_adapter(parent, target, rel_type, recref_adapter, recref_class)

    def test_later_letter_recref_adapter(self):
        # prepare data
        rel_type = 'aaa'
        parent = CofkUnionWork()
        parent.save()
        target = CofkUnionWork()
        target.save()
        recref_adapter = LaterLetterRecrefAdapter(parent)
        recref_class = CofkWorkWorkMap
        self._test_recref_form_adapter(parent, target, rel_type, recref_adapter, recref_class)

    def test_enclosure_manif_recref_adapter(self):
        rel_type = 'aaa'
        parent = CofkUnionManifestation()
        parent.save()
        target = CofkUnionManifestation()
        target.save()
        recref_adapter = EnclosureManifRecrefAdapter(parent)
        recref_class = CofkManifManifMap
        self._test_recref_form_adapter(parent, target, rel_type, recref_adapter, recref_class)

    def test_enclosure_manif_recref_adapter(self):
        rel_type = 'aaa'
        parent = CofkUnionManifestation()
        parent.save()
        target = CofkUnionManifestation()
        target.save()
        recref_adapter = EnclosedManifRecrefAdapter(parent)
        recref_class = CofkManifManifMap
        self._test_recref_form_adapter(parent, target, rel_type, recref_adapter, recref_class)

    def _test_recref_form_adapter(self, parent, target, rel_type, recref_adapter, recref_class):
        # test upsert_recref
        recref = recref_adapter.upsert_recref(rel_type, parent, target)
        recref.save()
        assert recref.recref_id
        # test find_recref_by_id
        db_recref = recref_adapter.find_recref_by_id(recref.recref_id)
        self.assertEqual(recref, db_recref)
        self.assertIsInstance(db_recref, recref_class)
        # test find_target_instance
        db_loc = recref_adapter.find_target_instance(target.pk)
        self.assertEqual(db_loc, target)
        # test find_targets_id_list
        id_list = recref_adapter.find_targets_id_list(rel_type)
        self.assertListEqual(list(id_list), [target.pk])

        # # test set_parent_target_instance
        new_recref = recref_class()
        recref_adapter.set_parent_target_instance(new_recref, parent, target)
        self.assertEqual(recref_adapter.get_target_id(new_recref), target.pk)

        # test find_recref_records
        recref_records = recref_adapter.find_recref_records(rel_type)
        self.assertEqual([recref], list(recref_records), )

        # test find_all_targets_by_rel_type
        targets = recref_adapter.find_all_targets_by_rel_type(rel_type)
        self.assertEqual([target], list(targets))
        target_id = recref_adapter.get_target_id(recref)
        self.assertEqual(target_id, target.pk)
