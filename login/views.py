from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render

from core.helper import exporter_serv


@login_required
def dashboard(request):
    return render(request, 'login/dashboard.html', {
        'is_exporting': exporter_serv.is_exporter_pending(),
    })

@login_required
def password_changed(request):
    return render(request, 'login/password-changed.html')

class EmloLoginView(LoginView):
    template_name = 'login/login.html'

    def form_valid(self, form):
        storage = messages.get_messages(self.request)
        for _ in storage:
            pass
        storage.used = True
        return super().form_valid(form)


class EmloLogoutView(LogoutView):
    next_page = 'login:gate'

    def dispatch(self, request, *args, **kwargs):
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = True
        return super().dispatch(request, *args, **kwargs)
