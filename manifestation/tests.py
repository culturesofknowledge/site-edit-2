import logging

from django.test import TransactionTestCase, RequestFactory

import manifestation.fixtures
from core.helper import model_serv
from core.test.test_export_header_values import MockResolver
from manifestation.models import CofkUnionManifestation
from manifestation.views import ManifSearchView
from siteedit2.serv.test_serv import EmloSeleniumTestCase, CommonSearchTests
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


class ManifestationTestCase(TransactionTestCase):

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

        self.assertQuerysetEqual(view.get_queryset(), [])


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
        self.find_search_btn().click()
