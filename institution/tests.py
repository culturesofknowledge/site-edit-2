import institution.fixtures
from institution.models import CofkInstitutionResourceMap
from institution.recref_adapter import InstResourceRecrefAdapter
from institution.views import InstMergeChoiceView
from siteedit2.serv.test_serv import MergeTests


class InstMergeTests(MergeTests):
    ResourceRecrefAdapter = InstResourceRecrefAdapter
    RecrefResourceMap = CofkInstitutionResourceMap
    ChoiceView = InstMergeChoiceView
    app_name = 'institution'

    @property
    def create_obj_fn(self):
        return institution.fixtures.create_person_obj

