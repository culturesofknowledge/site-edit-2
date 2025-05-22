import dateutil.parser
import logging
from dateutil.parser import ParserError
from django.core.exceptions import ObjectDoesNotExist
from suggestions.models import CofkSuggestions
from suggestions import utils as sug_utils
from person import person_suggestion_fields

log = logging.getLogger(__name__)

class PersonSuggestion:
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
            form_field = sug_utils.suggestion_fields_dict(person_suggestion_fields.suggestion_fields_map()).get(field, None)
            if form_field and sug_value:
                match field:
                    case 'Primary Name' | 'Alternative names' | 'Roles / titles':
                        form_values[form_field] = sug_value
                    case 'Gender':
                        if sug_value.lower() == "male" or sug_value.lower() == "m":
                            form_values[form_field] = "M"
                        elif sug_value.lower() == "female" or sug_value.lower() == "f":
                            form_values[form_field] = "F"
                    case "Date of birth" | "Date of death" | "Date when flourished":
                        try:
                            dt = dateutil.parser.parse(sug_value)
                            if dt.year:
                                form_values[f"{form_field}_year"] = dt.year
                            if dt.month:
                                form_values[f"{form_field}_month"] = (dt.month, dt.strftime("%b"))
                            if dt.day:
                                form_values[f"{form_field}_day"] = dt.day
                        except ParserError:
                            pass
        if form_values:
            form_values['editors_notes'] = f"From suggestion {sug.suggestion_id}\n{sug.suggestion_suggestion}"
        return form_values
