

from django.urls import path

from . import views

app_name = 'tombstone'
urlpatterns = [
    path('', views.home, name='home'),
    path('work', views.similar_work, name='work'),
    path('location', views.similar_location, name='location'),
]