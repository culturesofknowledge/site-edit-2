from django.urls import path

from core import lang_views
from core.lang_views import LanguageSearchView

app_name = 'lang'

urlpatterns = [
    path('search', LanguageSearchView.as_view(), name='search'),
    path('fav_add', lang_views.fav_add, name='fav_add'),
    path('fav_remove', lang_views.fav_remove, name='fav_remove'),
]
