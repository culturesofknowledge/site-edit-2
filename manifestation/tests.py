import logging

from django.test import TransactionTestCase, RequestFactory

from core.test.test_export_header_values import MockResolver
from manifestation.views import ManifSearchView

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
