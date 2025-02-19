import dateutil.parser
import logging
from dateutil.parser import ParserError
from django.core.exceptions import ObjectDoesNotExist
from suggestions.models import CofkSuggestions
from suggestions import utils as sug_utils
from institution import institution_suggestion_fields

log = logging.getLogger(__name__)

class InstitutionSuggestion:
    def __init__(self, suggestion_id):
        self.suggestion_id = suggestion_id

    def initial_form_values(self):
        form_values = {}
        try:
            sug = CofkSuggestions.objects.get(pk=self.suggestion_id)
            if sug.suggestion_status == "Resolved":
                log.debug(f"{sug.suggestion_type} suggestion id {sug.suggestion_id} is already in status {sug.suggestion_status}")
                return form_values
        except ObjectDoesNotExist:
            return form_values
        parsed_suggestion = sug.parsed_suggestion
        for field,sug_value in parsed_suggestion.items():
            form_field = sug_utils.suggestion_fields_dict(institution_suggestion_fields.suggestion_fields_map()).get(field, None)
            if form_field and sug_value:
                form_values[form_field] = sug_value
        if form_values:
            form_values['editors_notes'] = f"From suggestion {sug.suggestion_id}\n{sug.suggestion_suggestion}"
        return form_values
