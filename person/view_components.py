from core.helper.view_serv import FormDescriptor
from person import person_utils


class PersonFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return person_utils.get_recref_display_name(self.obj)

    @property
    def model_name(self):
        return 'Person'

    @property
    def id(self):
        return self.obj and self.obj.iperson_id
