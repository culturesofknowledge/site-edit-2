from django.contrib.auth.views import logout_then_login
from django.urls import path

from . import views
from .views import EmloLoginView

app_name = 'login'
urlpatterns = [
    path('dashboard', views.dashboard, name='example dashboard'),
    path('gate', EmloLoginView.as_view(), name='gate'),
    path('logout', logout_then_login, name='logout'),
]
