from django.test import TestCase

from core.export_excel.excel_header_values import WorkExcelHeaderValues
from siteedit2.utils.test_utils import EmloSeleniumTestCase
from work import work_utils
from work.models import CofkUnionWork


class TestWorkExcelHeaderValues(TestCase):

    def test_obj_to_values(self):
        work = CofkUnionWork(description='test')
        work.save()

        q_work = work_utils.clone_queryable_work(work, _return=True)


        hv = WorkExcelHeaderValues()
        values = hv.obj_to_values(q_work)

        self.assertGreater(len(values), 0)
