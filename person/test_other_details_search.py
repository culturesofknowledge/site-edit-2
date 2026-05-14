from django.test import TestCase, RequestFactory
from person.models import CofkUnionPerson, CofkPersonPersonMap
from person.views import PersonSearchView
from core import constant

class PersonOtherDetailsSearchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = PersonSearchView()

        # Create Person A (Ammonius)
        self.person_a = CofkUnionPerson(
            foaf_name='Ammonius',
            gender='M',
            is_organisation='N',
            iperson_id=1000,
            person_id='cofk_union_person-iperson_id:1000'
        )
        self.person_a.save()

        # Create Person B (Levinus Ammonius) - Sibling
        self.person_b = CofkUnionPerson(
            foaf_name='Levinus Ammonius',
            gender='M',
            is_organisation='N',
            person_aliases='Monastery Abbot', # "Monastery" in Titles/Roles
            iperson_id=1001,
            person_id='cofk_union_person-iperson_id:1001'
        )
        self.person_b.save()

        # Create relationship: Person A is sibling of Person B
        CofkPersonPersonMap.objects.create(
            person=self.person_a,
            related=self.person_b,
            relationship_type='sibling_of' 
        )

    def test_other_details_search_should_exclude_titles_roles(self):
        """
        Test that searching for 'Monastery' in 'Other details' should NOT find Person A
        if we exclude titles/roles from related person search.
        """
        request = self.factory.get('', {
            'names_and_titles': 'Ammonius',
            'names_and_titles_lookup': 'contains',
            'other_details': 'Monastery',
            'other_details_lookup': 'contains',
        })
        self.view.setup(request)
        queryset = self.view.get_queryset()
        
        self.assertNotIn(self.person_a, queryset)

    def test_other_details_search_should_include_names(self):
        """
        Test that searching for 'Levinus' in 'Other details' SHOULD find Person A
        because it matches 'Levinus' in Person B's name.
        """
        request = self.factory.get('', {
            'names_and_titles': 'Ammonius',
            'names_and_titles_lookup': 'contains',
            'other_details': 'Levinus',
            'other_details_lookup': 'contains',
        })
        self.view.setup(request)
        queryset = self.view.get_queryset()
        
        self.assertIn(self.person_a, queryset)
