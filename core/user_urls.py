from django.urls import path

from core.user_views import UserSearchView

app_name = 'user'

urlpatterns = [
    path('search', UserSearchView.as_view(), name='search'),
]
