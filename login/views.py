from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render


@login_required
def dashboard(request):
    return render(request, 'login/dashboard.html')

@login_required
def password_changed(request):
    return render(request, 'login/password-changed.html')

class EmloLoginView(LoginView):
    template_name = 'login/login.html'
