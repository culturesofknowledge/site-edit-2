from django.urls import path

from . import views
from .views import EmloLoginView

app_name = 'login'
urlpatterns = [
    path('dashboard', views.example_dashboard, name='example dashboard'),
    path('login_page', EmloLoginView.as_view()),
]
