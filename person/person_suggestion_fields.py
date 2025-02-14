
class PersonSuggestionFields:
    def suggestion_fields_map(self):
        return (
            ('Primary Name', 'foaf_name'),
            ('Gender', 'gender'),
            ('Alternative names', 'skos_altlabel'),
            ('Roles / titles', 'person_aliases'),
            ("Date of birth", 'date_of_birth'),
            ("Date of death", 'date_of_death'),
            ("Date when flourished", 'flourished')
        )

    def suggestion_fields(self):
        c = ()
        for b in self.suggestion_fields_map():
            c = c + (b[0],)
        return c

    def suggestion_fields_dict(self):
        x = {}
        for b in self.suggestion_fields_map():
            x[b[0]] = b[1]
        return x
