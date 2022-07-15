from django.urls import path

from . import views

app_name = 'location'
urlpatterns = [
    path('form', views.init_form, name='init_form'),
    path('form/<int:location_id>', views.full_form, name='full_form'),
    # TOBEREMOVE
    path('simple-list', views.simple_list, name='simple_list'),
    path('search', views.LocationSearchView.as_view(), name='search'),
]
