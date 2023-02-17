from . import views
from django.urls import path

from .views import CatalogueListView, RoleListView

app_name = 'lookups'
urlpatterns = [
    path('subjects/', CatalogueListView.as_view(), name='subjects'),
    path('roles/', RoleListView.as_view(), name='roles'),
    path('catalogues/', CatalogueListView.as_view(), name='catalogues'),
]

