from django.urls import path

from . import views

app_name = 'location'
urlpatterns = [
    path('get-location', views.get_location, name='get_location'),
]
