import datetime
import logging

from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404, redirect

from core.models import CofkUnionResource
from location.forms import LocationForm, LocationResourceForm
from location.models import CofkUnionLocation

log = logging.getLogger(__name__)


def init_form(request):
    loc_form = LocationForm(request.POST or None)
    if request.method == 'POST':
        if loc_form.is_valid():
            if loc_form.has_changed():
                log.info(f'location have been saved')
                _new_loc = loc_form.save()
                return redirect('location:full_form', _new_loc.location_id)
            else:
                log.debug('form have no change, skip record save')
            return redirect('location:search')

    return render(request, 'location/init_form.html', {'loc_form': loc_form, })


def full_form(request, location_id):
    loc = None
    location_id = location_id or request.POST.get('location_id')
    if location_id:
        loc = get_object_or_404(CofkUnionLocation, pk=location_id)

    loc_form = LocationForm(request.POST or None, instance=loc)

    loc_res_formset_factory = formset_factory(LocationResourceForm)
    loc_res_formset = loc_res_formset_factory(request.POST or None,
                                              prefix='loc_res',
                                              initial=[i.__dict__ for i in loc.resources.iterator()]
                                              )

    if request.method == 'POST':
        if loc_form.is_valid() and loc_res_formset.is_valid():
            log.info(f'location [{location_id}] have been saved')
            loc_form.save()

            res_forms = (f for f in loc_res_formset if f.has_changed())
            for form in res_forms:
                print(f'has changed : {form.changed_data}')
                form: LocationResourceForm
                form.instance: CofkUnionResource

                # fill resource value
                res = form.instance
                res.resource_id = form.cleaned_data.get('resource_id')

                now = datetime.datetime.now()
                if not res.creation_timestamp:
                    res.creation_timestamp = now
                res.change_timestamp = now

                user_val = 'user_val'  # KTODO to be define user val
                if not res.creation_user:
                    res.creation_user = user_val
                res.change_user = user_val

                form.save()
                loc.resources.add(res)

            return redirect('location:search')
        else:
            log.warning(f'something invalid {loc_form.is_valid()} / {loc_res_formset.is_valid()}')

    loc_res_formset.forms = list(reversed(loc_res_formset.forms))
    return render(request, 'location/full_form.html',
                  {'loc_form': loc_form,
                   'loc_res_formset': loc_res_formset,
                   'loc_id': location_id,
                   })


def search(request):
    locations = CofkUnionLocation.objects.iterator()
    return render(request, 'location/search.html',
                  {'locations': locations})
