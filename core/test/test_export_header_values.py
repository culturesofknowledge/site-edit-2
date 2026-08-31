from pathlib import Path

from django.test import TestCase

from cllib import path_utils
from core.constant import REL_TYPE_WORK_MATCHES
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
from work.models import CofkWorkWorkMap
from work.views import WorkSearchView, WorkCsvHeaderValues
from work.work_serv import DisplayableWork

# Column indices (0-based) of the "matched letters" pair in
# WorkExcelHeaderValues.get_header_list() - AX and AY respectively.
MATCH_IDS_COL = 49
MATCH_POSITION_COL = 50


class TestWorkExcelHeaderValues(TestCase):

    def test_obj_to_values(self):
        fixture_default_lookup_catalogue()
        hv = WorkExcelHeaderValues()
        work = DisplayableWork()
        work.save()
        values = hv.obj_to_values(work)

        self.assertGreater(len(values), 0)

    def test_obj_to_values_no_matches(self):
        """A letter with no match relationships at all has no match group to
        report, so both the IDs column (AX) and the position column (AY) are
        left blank."""
        fixture_default_lookup_catalogue()
        hv = WorkExcelHeaderValues()
        work = DisplayableWork(work_id='work_500728', iwork_id=500728)
        work.save()

        values = hv.obj_to_values(work)

        self.assertEqual(values[MATCH_IDS_COL], '')
        self.assertEqual(values[MATCH_POSITION_COL], '')

    def test_obj_to_values_matched_letters(self):
        """Matches column (AX) lists every letter ID in the group, including
        self, in ascending order; position column (AY) is self's 1-based
        position in that list - matching the reported ID 500728 example
        (31381; 400696; 500728 -> position 3)."""
        fixture_default_lookup_catalogue()

        work_31381 = DisplayableWork(work_id='work_31381', iwork_id=31381)
        work_31381.save()
        work_400696 = DisplayableWork(work_id='work_400696', iwork_id=400696)
        work_400696.save()
        work_500728 = DisplayableWork(work_id='work_500728', iwork_id=500728)
        work_500728.save()

        # Direct pairwise links from 500728, one in each direction, to
        # exercise both the forward and reverse halves of
        # find_matching_works_by_rel_type().
        CofkWorkWorkMap.objects.create(
            work_from=work_500728, work_to=work_31381,
            relationship_type=REL_TYPE_WORK_MATCHES,
            creation_user='test', change_user='test',
        )
        CofkWorkWorkMap.objects.create(
            work_from=work_400696, work_to=work_500728,
            relationship_type=REL_TYPE_WORK_MATCHES,
            creation_user='test', change_user='test',
        )

        hv = WorkExcelHeaderValues()
        values = hv.obj_to_values(work_500728)

        self.assertEqual(values[MATCH_IDS_COL], '31381; 400696; 500728')
        self.assertEqual(values[MATCH_POSITION_COL], 3)


class MockResolver:
    def __init__(self, app_name):
        self.app_name = app_name


class MockUser:
    is_authenticated = False
    pk = None


class MockRequest:
    def __init__(self, app_name):
        self.resolver_match = MockResolver(app_name)
        self.GET = {}
        self.user = MockUser()


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
