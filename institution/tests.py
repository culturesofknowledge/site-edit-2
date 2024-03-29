import institution.fixtures
from core.helper.test_serv import MergeTests
from institution.models import CofkInstitutionResourceMap
from institution.recref_adapter import InstResourceRecrefAdapter
from institution.views import InstMergeChoiceView


class InstMergeTests(MergeTests):
    ResourceRecrefAdapter = InstResourceRecrefAdapter
    RecrefResourceMap = CofkInstitutionResourceMap
    ChoiceView = InstMergeChoiceView
    app_name = 'institution'

    @property
    def create_obj_fn(self):
        return institution.fixtures.create_person_obj

