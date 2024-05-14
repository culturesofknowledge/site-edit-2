from django.urls import path

from core import misc_views

app_name = 'misc'

urlpatterns = [
    path('trigger-export', misc_views.trigger_export, name='trigger_export'),
]
