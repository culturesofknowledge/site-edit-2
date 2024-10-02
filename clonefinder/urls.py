from django.urls import path

from . import views

app_name = 'clonefinder'
urlpatterns = [
    path('', views.home, name='home'),
    path('work', views.similar_work, name='work'),
    path('location', views.similar_location, name='location'),
    path('person', views.similar_person, name='person'),
    path('inst', views.similar_inst, name='inst'),
    path('trigger_inst', views.trigger_inst_clustering, name='trigger_inst'),
    path('trigger_location', views.trigger_location_clustering, name='trigger_location'),
    path('trigger_person', views.trigger_person_clustering, name='trigger_person'),
    path('trigger_work', views.trigger_work_clustering, name='trigger_work'),
]
