from core.helper.view_serv import FormDescriptor
from institution import inst_serv


class InstFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return inst_serv.get_recref_display_name(self.obj)

    @property
    def model_name(self):
        return 'Institution'
