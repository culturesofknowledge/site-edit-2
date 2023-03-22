from core.helper.view_utils import FormDescriptor


class LocationFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return self.obj.location_name or self.obj.location_id

    @property
    def model_name(self):
        return 'Location'
