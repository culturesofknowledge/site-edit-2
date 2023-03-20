from pathlib import Path

from django.test import TestCase

from core.export_data.excel_header_values import WorkExcelHeaderValues
from core.helper import file_utils
from core.helper.view_components import DownloadCsvHandler
from institution.models import CofkUnionInstitution
from institution.views import InstSearchView, InstCsvHeaderValues
from location.models import CofkUnionLocation
from location.views import LocationCsvHeaderValues, LocationSearchView
from person.models import CofkUnionPerson
from person.views import PersonSearchView, PersonCsvHeaderValues
from work import work_utils
from work.models import CofkUnionWork, CofkUnionQueryableWork
from work.views import WorkSearchView, WorkCsvHeaderValues


def fixture_queryable_work() -> CofkUnionQueryableWork:
    work = CofkUnionWork(description='test')
    work.save()

    q_work = work_utils.clone_queryable_work(work, _return=True)
    return q_work


class TestWorkExcelHeaderValues(TestCase):

    def test_obj_to_values(self):
        hv = WorkExcelHeaderValues()
        values = hv.obj_to_values(fixture_queryable_work())

        self.assertGreater(len(values), 0)


class TestDownloadCsvHandler(TestCase):

    def assert_with_search_view(self, search_view, header_values, expected_len):
        file_path = file_utils.create_new_tmp_file_path(prefix='search_results_', suffix='.csv')
        csv_handler = DownloadCsvHandler(header_values)
        csv_handler.create_csv_file(search_view.get_queryset_by_request_data({}, sort_by=''), file_path)
        self.assertEqual(
            len(Path(file_path).read_text().splitlines()),
            expected_len
        )

    def test_person_csv(self):
        person = CofkUnionPerson(foaf_name='aa')
        person.save()
        self.assert_with_search_view(PersonSearchView(), PersonCsvHeaderValues(), 2)

    def test_work_csv(self):
        fixture_queryable_work().save()
        self.assert_with_search_view(WorkSearchView(), WorkCsvHeaderValues(), 2)

    def test_inst_csv(self):
        inst = CofkUnionInstitution(institution_name='aa')
        inst.save()
        self.assert_with_search_view(InstSearchView(), InstCsvHeaderValues(), 2)

    def test_location_csv(self):
        location = CofkUnionLocation(location_name='aa')
        location.save()
        self.assert_with_search_view(LocationSearchView(), LocationCsvHeaderValues(), 2)