from django.contrib.auth.views import logout_then_login, PasswordChangeView
from django.urls import path

from . import views
from .views import EmloLoginView, password_changed

app_name = 'login'
urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('gate', EmloLoginView.as_view(), name='gate'),
    path('change-password', PasswordChangeView.as_view(template_name='login/change-password.html',
                                      success_url='password-changed'), name='change-password'),
    path('password-changed', password_changed, name='password-changed'),
    path('logout', logout_then_login, name='logout'),
]
