import logging

from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from location.forms import LocationForm, LocationResourceForm
from location.models import CofkCollectLocation, CofkCollectLocationResource, CofkUnionLocation

log = logging.getLogger(__name__)


def init_form(request):
    loc_form = LocationForm(request.POST or None)
    if request.method == 'POST':
        if loc_form.is_valid():
            if loc_form.has_changed():
                log.info(f'location have been saved')
                _new_loc = loc_form.save()
                return redirect('location:search')
                # return redirect('location:full_form', _new_loc.location_id) # KTODO to be fix
            else:
                log.debug('form have no change, skip record save')
            return redirect('location:search')

    return render(request, 'location/init_form.html', {'loc_form': loc_form, })


def full_form(request, location_id):
    loc = None
    location_id = location_id or request.POST.get('location_id')
    if location_id:
        loc = get_object_or_404(CofkCollectLocation, pk=location_id)

    loc_form = LocationForm(request.POST or None, instance=loc)

    loc_res_formset_factory = formset_factory(LocationResourceForm)
    loc_res_formset = loc_res_formset_factory(request.POST or None,
                                              prefix='loc_res',
                                              initial=[i.__dict__ for i in loc.resources.iterator()]
                                              )
    loc_res_formset.forms = list(reversed(loc_res_formset.forms))
    if request.method == 'POST':
        if loc_form.is_valid() and loc_res_formset.is_valid():
            log.info(f'location [{location_id}] have been saved')
            loc_form.save()
            for form in loc_res_formset:
                form: LocationResourceForm

                form.instance: CofkCollectLocationResource
                form.instance.resource_id = form.cleaned_data.get('resource_id')
                form.instance.location_id = location_id

                if form.has_changed():
                    print(f'has changed : {form.changed_data}')
                    form.save()
            return redirect('location:search')
        else:
            log.warning(f'something invalid {loc_form.is_valid()} / {loc_res_formset.is_valid()}')

    return render(request, 'location/full_form.html',
                  {'loc_form': loc_form,
                   'loc_res_formset': loc_res_formset,
                   'loc_id': location_id,
                   })


def search(request):
    locations = CofkUnionLocation.objects.iterator()
    return render(request, 'location/search.html',
                  {'locations': locations})
