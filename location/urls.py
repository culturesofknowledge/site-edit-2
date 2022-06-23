from django.urls import path

from . import views

app_name = 'location'
urlpatterns = [
    path('form', views.form, name='form'),
    path('form/<int:location_id>', views.form, name='form_by_id'),
    path('search', views.search, name='search'),
]
