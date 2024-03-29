from django.urls import path

from .views import CatalogueListView, RoleListView, SubjectListView, OrgTypeListView, SavedQueries

app_name = 'list'
urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subjects'),
    path('roles/', RoleListView.as_view(), name='roles'),
    path('catalogues/', CatalogueListView.as_view(), name='catalogues'),
    path('orgtypes/', OrgTypeListView.as_view(), name='orgtypes'),
    path('queries/', SavedQueries.as_view(), name='savedqueries')
]
