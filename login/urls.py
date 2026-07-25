from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy

from . import views
from .views import EmloLoginView, EmloLogoutView, password_changed

app_name = 'login'
urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('gate', EmloLoginView.as_view(), name='gate'),
    path('change-password', PasswordChangeView.as_view(template_name='login/change-password.html',
                                      success_url='password-changed'), name='change-password'),
    path('password-changed', password_changed, name='password-changed'),
    path('logout', EmloLogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='login/password-reset.html',
        email_template_name='login/password-reset-email.txt',
        success_url=reverse_lazy('login:password_reset_done'),
    ), name='password-reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='login/password-reset-done.html',
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='login/password-reset-confirm.html',
        success_url=reverse_lazy('login:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='login/password-reset-complete.html',
    ), name='password_reset_complete'),
]
