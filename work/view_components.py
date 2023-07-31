from core.helper.view_serv import FormDescriptor
from work import work_serv


class WorkFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return work_serv.get_recref_display_name(self.obj)

    @property
    def model_name(self):
        return 'Work'

    @property
    def id(self):
        return self.obj and self.obj.iwork_id
