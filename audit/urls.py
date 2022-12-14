from . import views
from django.urls import path

app_name = 'audit'
urlpatterns = [
    path('search', views.AuditSearchView.as_view(), name='search'),
]
