from suggestion.models import CofkSuggestions
import dateutil.parser


class PersonSuggestion:
    def __init__(self, suggestion_id):
        self.suggestion_id = suggestion_id

    def suggestion_fields(self):
        return {
            'Primary Name': 'foaf_name',
            'Gender': 'gender',
            'Alternative names': 'skos_altlabel',
            'Roles / titles': 'person_aliases',
            "Date of birth": 'date_of_birth',
            "Date of death": 'date_of_death',
            "Date when flourished": 'flourished'
        }

    def initial_form_values(self):
        sug = CofkSuggestions.objects.get(pk=self.suggestion_id)
        parsed_suggestion = sug.parsed_suggestion
        form_values = {}
        for field in sug.fields():
            form_field = self.suggestion_fields.get(field, None)
            sug_value = parsed_suggestion.get(field, None)
            if form_field and sug_value:
                match field:
                    case 'Primary Name', 'Gender', 'Alternative names', 'Roles / titles':
                        form_values[form_field] = sug_value
                    case "Date of birth", "Date of death", "Date when flourished":
                        dt = dateutil.parser.parse(sug_value)
                        if dt.year:
                            form_values[f"#{form_field}_year"] = dt.year
                        if dt.month:
                            form_values[f"#{form_field}_month"] = dt.month
                        if dt.day:
                            form_values[f"#{form_field}_day"] = dt.day
        return form_values



