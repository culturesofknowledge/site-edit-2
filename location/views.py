import itertools
import logging
from typing import Iterable, Union, Callable, List, Tuple

from django.forms import formset_factory, BaseForm, BaseFormSet
from django.shortcuts import render, get_object_or_404, redirect

from core.helper.model_utils import RecordTracker
from core.helper.view_utils import SearchResultRenderer, BasicSearchView
from location.forms import LocationForm, LocationResourceForm, LocationCommentForm, GeneralSearchFieldset
from location.models import CofkUnionLocation

log = logging.getLogger(__name__)


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


FormOrFormSet = Union[BaseForm, BaseFormSet]


def to_forms(form_or_formset: FormOrFormSet):
    if isinstance(form_or_formset, BaseForm):
        return [form_or_formset]
    elif isinstance(form_or_formset, BaseFormSet):
        return form_or_formset.forms
    else:
        raise ValueError(f'unknown form type {type(form_or_formset)}')


def flat_forms(form_formsets: Iterable[FormOrFormSet]):
    forms = map(to_forms, form_formsets)
    return itertools.chain.from_iterable(forms)


def flat_changed_forms(form_formsets: Iterable[FormOrFormSet]):
    forms = flat_forms(form_formsets)
    return (f for f in forms if f.has_changed())


def update_current_user_timestamp(user, form_formsets: Iterable[FormOrFormSet]):
    forms = flat_changed_forms(form_formsets)
    forms = (f for f in forms if isinstance(f, RecordTracker))
    for f in forms:
        f.update_current_user_timestamp(user)


def save_changed_forms(form_formsets: Iterable[FormOrFormSet]):
    for f in flat_changed_forms(form_formsets):
        f.save()


def create_formset(form_class, post_data=None, prefix=None, many_related_manager=None):
    initial = [i.__dict__ for i in many_related_manager.iterator()]
    return formset_factory(form_class)(
        post_data or None,
        prefix=prefix,
        initial=initial
        # KTODO try queryset=
    )


def save_formset(formset: BaseFormSet,
                 many_related_manager=None,
                 model_id_name=None,
                 form_id_name=None):
    _forms = (f for f in formset if f.has_changed())
    for form in _forms:
        log.debug(f'form has changed : {form.changed_data}')

        # set mode_id
        if model_id_name:
            if hasattr(form.instance, model_id_name):
                form_id_name = form_id_name or model_id_name
                if not hasattr(form, 'cleaned_data'):
                    breakpoint()  # KTODO is this happen??
                if form_id_name in form.cleaned_data:
                    setattr(form.instance, model_id_name,
                            form.cleaned_data.get(form_id_name))
                else:
                    log.warning(f'form_id_name[{model_id_name}] not found in form_clean_data[{form.cleaned_data}]')

            else:
                log.warning(f'mode_id_name[{model_id_name}] not found in form.instance')

        # save form
        form.save()

        # bind many-to-many relation
        if many_related_manager:
            many_related_manager.add(form.instance)


def full_form(request, location_id):
    loc = None
    location_id = location_id or request.POST.get('location_id')
    if location_id:
        loc = get_object_or_404(CofkUnionLocation, pk=location_id)

    loc_form = LocationForm(request.POST or None, instance=loc)
    # KTODO how to handle upload image

    res_formset = create_formset(LocationResourceForm, post_data=request.POST,
                                 prefix='loc_res', many_related_manager=loc.resources)
    comment_formset = create_formset(LocationCommentForm, post_data=request.POST,
                                     prefix='loc_comment', many_related_manager=loc.comments)

    def _render_full_form():
        res_formset.forms = list(reversed(res_formset.forms))
        return render(request, 'location/full_form.html',
                      {'loc_form': loc_form,
                       'res_formset': res_formset,
                       'comment_formset': comment_formset,
                       'loc_id': location_id,
                       })

    if request.method == 'POST':
        form_formsets = [loc_form, res_formset, comment_formset]
        print([f.is_valid() for f in form_formsets])

        if not all(f.is_valid() for f in form_formsets):
            log.warning(f'something invalid {loc_form.is_valid()} / {res_formset.is_valid()}')
            return _render_full_form()

        update_current_user_timestamp(request.user.username, form_formsets)

        # update res instead
        save_formset(res_formset, loc.resources, model_id_name='resource_id')

        # update comment instead
        save_formset(comment_formset, loc.comments, model_id_name='comment_id')

        loc_form.save()
        log.info(f'location [{location_id}] have been saved')
        return redirect('location:search')

    return _render_full_form()


class LocationSearchResultRenderer(SearchResultRenderer):

    @property
    def template_name(self):
        return 'location/search_result.html'


class LocationSearchView(BasicSearchView):
    paginate_by = 4

    @property
    def record_renderer(self) -> Callable:
        return LocationSearchResultRenderer

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request.GET)]

    @property
    def sort_by_choices(self) -> List[Tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
            ('-location_name', 'Location Name desc',),
            ('location_name', 'Location Name asc',),
        ]

    def get_queryset(self):
        queryset = CofkUnionLocation.objects
        if sort_by := self.request.GET.get('sort_by'):
            queryset = queryset.order_by(sort_by)
        return queryset.all()

    @property
    def title(self) -> str:
        return 'Location'
