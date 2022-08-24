from django.shortcuts import render


def init_form(request):
    loc_form = LocationForm(request.POST or None)
    if request.method == 'POST':
        if loc_form.is_valid():
            if loc_form.has_changed():
                log.info(f'location have been saved')
                loc_form.instance.update_current_user_timestamp(request.user.username)
                _new_loc = loc_form.save()
                return redirect('location:full_form', _new_loc.location_id)
            else:
                log.debug('form have no change, skip record save')
            return redirect('location:search')

    return render(request, 'location/init_form.html', {'loc_form': loc_form, })
