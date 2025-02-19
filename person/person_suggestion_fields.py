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
