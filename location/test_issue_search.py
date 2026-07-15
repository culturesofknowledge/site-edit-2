from django.test import TestCase
from location.models import CofkUnionLocation
from location.views import LocationSearchView

class LocationSearchIssueTest(TestCase):
    def test_name_ends_with_england(self):
        # Create a location with primary name ending with England and no synonyms
        loc1 = CofkUnionLocation.objects.create(
            location_name='London, England',
            location_synonyms='',
            creation_user='test',
            change_user='test'
        )
        # Create a location with primary name NOT ending with England but synonym ending with England
        loc2 = CofkUnionLocation.objects.create(
            location_name='London',
            location_synonyms='Londinium, England',
            creation_user='test',
            change_user='test'
        )
        # Create a location with neither ending with England
        loc3 = CofkUnionLocation.objects.create(
            location_name='Paris, France',
            location_synonyms='Lutetia',
            creation_user='test',
            change_user='test'
        )

        search_view = LocationSearchView()
        
        # Search for "Name ends with England"
        request_data = {
            'location_name': 'England',
            'location_name_lookup': 'ends_with'
        }
        
        qs = search_view.get_queryset_by_request_data(request_data)
        results = list(qs)

        result_names = [loc.location_name for loc in results]

        # Current behavior (buggy): only loc2 will be found because it only searches synonyms
        # Desired behavior: both loc1 and loc2 should be found
        self.assertIn('London, England', result_names, "Primary name ending with England should be found")
        # https://github.com/culturesofknowledge/site-edit-2/commit/7486c1634e937bea6287825cb16f9bbf620fbe41
        # this commit changed search behaviour
        # self.assertIn('London', result_names, "Synonym ending with England should be found")
        self.assertEqual(len(results), 1)

    def test_name_does_not_end_with_england(self):
        # Create a location with primary name ending with England
        CofkUnionLocation.objects.create(
            location_name='London, England',
            location_synonyms='',
            creation_user='test',
            change_user='test'
        )
        # Create a location with synonym ending with England
        CofkUnionLocation.objects.create(
            location_name='London',
            location_synonyms='Londinium, England',
            creation_user='test',
            change_user='test'
        )
        # Create a location with neither ending with England
        CofkUnionLocation.objects.create(
            location_name='Paris, France',
            location_synonyms='Lutetia',
            creation_user='test',
            change_user='test'
        )

        search_view = LocationSearchView()
        
        # Search for "Name does not end with England"
        request_data = {
            'location_name': 'England',
            'location_name_lookup': 'not_end_with'
        }
        
        qs = search_view.get_queryset_by_request_data(request_data)
        results = list(qs)
        
        result_names = [loc.location_name for loc in results]
        
        # Desired behavior: only 'Paris, France' should be found
        self.assertNotIn('London, England', result_names)
        # https://github.com/culturesofknowledge/site-edit-2/commit/7486c1634e937bea6287825cb16f9bbf620fbe41
        # this commit changed search behaviour
        # self.assertNotIn('London', result_names)
        self.assertIn('Paris, France', result_names)
        self.assertEqual(len(results), 2)
