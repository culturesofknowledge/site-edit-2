from django.urls import path

from . import views

app_name = 'location'
urlpatterns = [
    path('form', views.init_form, name='init_form'),
    path('form/<int:location_id>', views.full_form, name='full_form'),
    path('search', views.search, name='search'),
]
