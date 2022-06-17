from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from location.forms import LocationForm


def form(request):
    return HttpResponse("It is location form page.")


def get_location(request):
    loc_form = LocationForm(request.POST or None)
    if request.method == 'POST':
        if loc_form.is_valid():
            loc_form.save()
            # KTODO do something e.g. validate and save
            return HttpResponse("Ha Ha Ha Ha....")

    return render(request, 'location/get_location.html', {'form': loc_form})
