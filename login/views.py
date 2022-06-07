from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

@login_required(login_url='/login/login_page')
def example_dashboard(request):
    # return HttpResponse("It is example dashboard page.")
    return render(request, 'login/dashboard.html')


class EmloLoginView(LoginView):
    template_name = 'login/login.html'
