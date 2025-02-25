from pathlib import Path

from django.test import TestCase

from cllib import path_utils
from core.export_data.excel_header_values import WorkExcelHeaderValues
from core.fixtures import fixture_default_lookup_catalogue
from core.helper.view_components import DownloadCsvHandler
from institution.models import CofkUnionInstitution
from institution.views import InstSearchView, InstCsvHeaderValues
from location.models import CofkUnionLocation
from location.views import LocationCsvHeaderValues, LocationSearchView
from person.models import CofkUnionPerson
from person.views import PersonSearchView, PersonCsvHeaderValues
from work.fixtures import fixture_work_simple_a
from work.views import WorkSearchView, WorkCsvHeaderValues
from work.work_serv import DisplayableWork


class TestWorkExcelHeaderValues(TestCase):

    def test_obj_to_values(self):
        fixture_default_lookup_catalogue()
        hv = WorkExcelHeaderValues()
        work = DisplayableWork()
        work.save()
        values = hv.obj_to_values(work)

        self.assertGreater(len(values), 0)


class MockResolver:
    def __init__(self, app_name):
        self.app_name = app_name


class MockRequest:
    def __init__(self, app_name):
        self.resolver_match = MockResolver(app_name)


class TestDownloadCsvHandler(TestCase):

    def assert_with_search_view(self, search_view, header_values, expected_len):
        file_path = path_utils.create_tmp_path(prefix='search_results_', suffix='.csv')
        csv_handler = DownloadCsvHandler(header_values)
        csv_handler.create_csv_file(search_view.get_queryset_by_request_data({}, sort_by=''), file_path)
        self.assertEqual(
            len(Path(file_path).read_text().splitlines()),
            expected_len
        )

    def test_person_csv(self):
        person = CofkUnionPerson(foaf_name='aa')
        person.save()
        self.assert_with_search_view(PersonSearchView(request=MockRequest('person')), PersonCsvHeaderValues(), 2)

    def test_work_csv(self):
        fixture_work_simple_a()
        fixture_default_lookup_catalogue()
        self.assert_with_search_view(WorkSearchView(request=MockRequest('work')), WorkCsvHeaderValues(), 2)

    def test_inst_csv(self):
        inst = CofkUnionInstitution(institution_name='aa')
        inst.save()
        self.assert_with_search_view(InstSearchView(request=MockRequest('repository')), InstCsvHeaderValues(), 2)

    def test_location_csv(self):
        location = CofkUnionLocation(location_name='aa')
        location.save()
        self.assert_with_search_view(LocationSearchView(request=MockRequest('location')), LocationCsvHeaderValues(), 2)
