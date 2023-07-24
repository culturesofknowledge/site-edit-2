import manifestation.fixtures
from core.helper import model_serv
from manifestation.models import CofkUnionManifestation
from siteedit2.utils.test_utils import EmloSeleniumTestCase, CommonSearchTests
from work.models import CofkUnionWork


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
