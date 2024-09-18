

from django.urls import path

from . import views

app_name = 'tombstone'
urlpatterns = [
    path('', views.home, name='home'),
    path('work', views.similar_work, name='work'),
    path('location', views.similar_location, name='location'),
    path('person', views.similar_person, name='person'),
    path('inst', views.similar_inst, name='inst'),
]