from django.template.loader import render_to_string


class CompactItemRenderer:
    def __init__(self, record, record_name='record'):
        self.record = record
        self.record_name = record_name

    def __call__(self, *args, **kwargs):
        return render_to_string(self.template_name,
                                context={self.record_name: self.record})

    @property
    def template_name(self):
        raise NotImplementedError('please define search result template')
