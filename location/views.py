from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.


def form(request):
    return HttpResponse("It is location form page.")
