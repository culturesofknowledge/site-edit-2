from django.test import TestCase, RequestFactory
from person.views import PersonSearchView

class PersonSimplifiedQueryTest(TestCase):
    def test_simplified_query_date_range(self):
        request_factory = RequestFactory()
        view = PersonSearchView()
        view.setup(request_factory.get('', data={
            'birth_year_from': '1740',
            'birth_year_to': '1740',
        }))
        
        simplified_query = view.simplified_query
        print(f"Simplified query: {simplified_query}")
        self.assertIn('Born between 01/01/1740 and 31/12/1740', simplified_query)

    def test_simplified_query_date_from_only(self):
        request_factory = RequestFactory()
        view = PersonSearchView()
        view.setup(request_factory.get('', data={
            'birth_year_from': '1740',
        }))
        
        simplified_query = view.simplified_query
        print(f"Simplified query: {simplified_query}")
        self.assertIn('Born after 01/01/1740', simplified_query)

    def test_simplified_query_date_to_only(self):
        request_factory = RequestFactory()
        view = PersonSearchView()
        view.setup(request_factory.get('', data={
            'birth_year_to': '1740',
        }))
        
        simplified_query = view.simplified_query
        print(f"Simplified query: {simplified_query}")
        self.assertIn('Born before 31/12/1740', simplified_query)
