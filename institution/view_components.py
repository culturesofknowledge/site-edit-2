from core.helper.view_utils import FormDescriptor
from institution import inst_utils


class InstFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return inst_utils.get_recref_display_name(self.obj)

    @property
    def model_name(self):
        return 'Institution'
