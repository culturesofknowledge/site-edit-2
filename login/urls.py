from django.urls import path

from . import views
from .views import EmloLoginView

app_name = 'login'
urlpatterns = [
    path('dashboard', views.example_dashboard, name='example dashboard'),
    path('gate', EmloLoginView.as_view(), name='gate'),
    path('logout', views.logout_then_login, name='logout'),
]
