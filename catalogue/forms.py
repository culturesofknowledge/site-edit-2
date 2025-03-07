from core.form_label_maps import field_label_map
from core.helper import form_serv
from core.helper.form_serv import BasicSearchFieldset, SearchCharField


class CatalogueSearchFieldset(BasicSearchFieldset):

    title = 'Search Catalogue'

    template_name = 'catalogue/component/catalogue_search_fieldset.html'

    code = SearchCharField(label=field_label_map['catalogue']['catalogue_code'],
                                       help_text='')
    code_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    name = SearchCharField(label=field_label_map['catalogue']['catalogue_name'],
                                       help_text='')
    name_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)

    status = SearchCharField(label=field_label_map['catalogue']['publish_status'],
                                          help_text='')

    status_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)