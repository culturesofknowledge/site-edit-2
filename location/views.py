import logging

from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from location.forms import LocationForm
from location.models import CofkCollectLocation

log = logging.getLogger(__name__)


def form(request, location_id=None):
    loc = None
    location_id = location_id or request.POST.get('location_id')
    if location_id:
        loc = get_object_or_404(CofkCollectLocation, pk=location_id)

    loc_form = LocationForm(request.POST or None, instance=loc)
    if request.method == 'POST':
        if loc_form.is_valid():
            if loc_form.has_changed():
                log.info(f'location [{location_id}] have been saved')
                loc_form.save()
            else:
                log.debug('form have no change, skip record save')
            return redirect('location:search')

    return render(request, 'location/main_form.html', {'form': loc_form, })


def search(request):
    locations = CofkCollectLocation.objects.iterator()
    return render(request, 'location/search.html',
                  {'locations': locations})
