from django.urls import path

from . import views
from .views import EmloLoginView

urlpatterns = [
    path('dashboard', views.example_dashboard, name='example dashboard'),
    path('login_page', EmloLoginView.as_view()),
]
