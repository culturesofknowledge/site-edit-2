import logging

from django.test import RequestFactory, TestCase

import manifestation.fixtures
import manifestation.fixtures
from core.helper import model_serv
from core.helper.test_serv import EmloSeleniumTestCase, CommonSearchTests
from core.test.test_export_header_values import MockResolver
from manifestation import manif_serv
from manifestation.models import CofkUnionManifestation
from manifestation.views import ManifSearchView
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


class ManifestationTestCase(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_no_results(self):
        """
        This test makes sure that a request to manifestation root URL returns
        ane empty queryset.
        """
        request = self.factory.get("/manif")
        request.resolver_match = MockResolver('manifestation')

        view = ManifSearchView()
        view.setup(request)

        self.assertQuerySetEqual(view.get_queryset(), [])


class CreateManifIdTestCase(TestCase):

    def create_work(self, iwork_id) -> CofkUnionWork:
        work = CofkUnionWork(work_id=f'work_id_{iwork_id}', iwork_id=iwork_id)
        work.save()
        return work

    def test_letter_suffix(self):
        self.assertEqual('a', manif_serv.to_letter_suffix(0))
        self.assertEqual('z', manif_serv.to_letter_suffix(25))
        self.assertEqual('aa', manif_serv.to_letter_suffix(26))

    def test_create_manif_id__restart_for_each_work(self):
        for iwork_id in (10, 11):
            work = self.create_work(iwork_id)
            for expected in ('a', 'b', 'c', 'd'):
                manif_id = manif_serv.create_manif_id(iwork_id)
                self.assertEqual(f'W{iwork_id}-{expected}', manif_id)
                CofkUnionManifestation.objects.create(
                    manifestation_id=manif_id, work=work,
                    creation_user='tester', change_user='tester',
                )

    def test_create_manif_id__reserved_ids_are_skipped(self):
        """Ids handed out but not saved yet (bulk created uploads) must not be reused."""
        self.create_work(12)
        used = []
        for expected in ('a', 'b', 'c', 'd'):
            manif_id = manif_serv.create_manif_id(12, used_manif_ids=used)
            self.assertEqual(f'W12-{expected}', manif_id)
            used.append(manif_id)

    def test_create_manif_id__skips_existing_suffix(self):
        work = self.create_work(13)
        CofkUnionManifestation.objects.create(
            manifestation_id='W13-a', work=work,
            creation_user='tester', change_user='tester',
        )
        self.assertEqual('W13-b', manif_serv.create_manif_id(13))


def prepare_manif_records() -> list[CofkUnionManifestation]:
    work = CofkUnionWork(work_id='work_id_a')
    work.save()

    manif_dict_a = manifestation.fixtures.manif_dict_a.copy()
    manif_dict_a['work_id'] = work.work_id
    return model_serv.create_multi_records_by_dict_list(CofkUnionManifestation, [
        manif_dict_a
    ])


# Create your tests here.
class ManifSearchTests(EmloSeleniumTestCase, CommonSearchTests):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_common_search_test(self, 'manif:search', prepare_manif_records)

    def test_normal(self):
        self.goto_search_page()

    def test_search__GET(self):
        records = self.prepare_records()
        self.goto_search_page()
        self.find_search_btn().click()
        self.assert_search_page(num_row_show=len(records), num_total=len(records))
