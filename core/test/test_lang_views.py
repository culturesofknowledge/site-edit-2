from django.test import TestCase
from django.urls import reverse

from core import constant
from core.helper import perm_serv
from core.models import CofkUnionFavouriteLanguage, Iso639LanguageCode
from login.fixtures import create_test_user


class FavouriteLanguageTests(TestCase):

    def setUp(self):
        self.lang = Iso639LanguageCode.objects.create(code_639_3='lat', code_639_1='la',
                                                      language_name='Latin', language_id=99001)

    def is_favourite(self):
        return CofkUnionFavouriteLanguage.objects.filter(language_code=self.lang).exists()

    def login_with_perm(self):
        user = create_test_user('lang_admin')
        user.user_permissions.add(perm_serv.get_perm_by_full_name(constant.PM_CHANGE_LANGUAGE))
        self.client.force_login(user)

    def test_add_requires_login(self):
        response = self.client.post(reverse('lang:fav_add'), {'code_639_3': 'lat'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.is_favourite())

    def test_remove_requires_permission(self):
        CofkUnionFavouriteLanguage.objects.create(language_code=self.lang)
        self.client.force_login(create_test_user('viewer'))

        self.client.post(reverse('lang:fav_remove'), {'code_639_3': 'lat'})

        self.assertTrue(self.is_favourite())

    def test_add_and_remove_with_permission(self):
        self.login_with_perm()

        self.assertEqual(self.client.post(reverse('lang:fav_add'), {'code_639_3': 'lat'}).status_code, 200)
        self.assertTrue(self.is_favourite())

        self.assertEqual(self.client.post(reverse('lang:fav_remove'), {'code_639_3': 'lat'}).status_code, 200)
        self.assertFalse(self.is_favourite())

    def test_missing_code_is_bad_request(self):
        self.login_with_perm()

        self.assertEqual(self.client.post(reverse('lang:fav_add')).status_code, 400)
        self.assertEqual(self.client.post(reverse('lang:fav_remove')).status_code, 400)

    def test_get_not_allowed(self):
        self.login_with_perm()
        self.assertEqual(self.client.get(reverse('lang:fav_add')).status_code, 405)
