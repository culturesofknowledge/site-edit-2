from django.urls import path
from .views import suggestion_person, suggestion_publication
from .views import suggestion_institution, suggestion_location
from .views import suggestion_edit, suggestion_delete, suggestion_show
from .views import suggestion_all

app_name = 'suggestions'
urlpatterns = [
    path('',            suggestion_all,         name='suggestion_all'),
    path('all',         suggestion_all,         name='suggestion_all'),
    path('person',      suggestion_person,      name='suggestion_person'),
    path('location',    suggestion_location,    name='suggestion_location'),
    path('publication', suggestion_publication, name='suggestion_publication'),
    path('institution', suggestion_institution, name='suggestion_institution'),
    path('<int:suggestion_id>',       suggestion_show,   name='suggestion_show'),
    path('edit/<int:suggestion_id>',   suggestion_edit,   name='suggestion_edit'),
    path('delete/<int:suggestion_id>', suggestion_delete, name='suggestion_delete'),
]
