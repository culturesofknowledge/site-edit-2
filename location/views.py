import itertools
import logging
from typing import Iterable, Union, List, Tuple, Type, Callable

from django.conf import settings
from django.forms import formset_factory, BaseForm, BaseFormSet, ModelForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from core.helper import model_utils
from core.helper.model_utils import RecordTracker
from core.helper.renderer import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_utils import BasicSearchView
from core.services import media_service
from location.forms import LocationForm, LocationResourceForm, LocationCommentForm, GeneralSearchFieldset, \
    LocationImageForm, LocUploadImageForm
from location.models import CofkUnionLocation
from location.renderer import LocationCompactSearchResultsRenderer, LocationTableSearchResultsRenderer
from uploader.models import CofkUnionImage

log = logging.getLogger(__name__)
FormOrFormSet = Union[BaseForm, BaseFormSet]


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
    forms = (f for f in forms if isinstance(f, ModelForm))
    records = (f.instance for f in forms if isinstance(f.instance, RecordTracker))
    for r in records:
        r.update_current_user_timestamp(user)


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


def save_formset(forms: Iterable[ModelForm],
                 many_related_manager=None,
                 model_id_name=None,
                 form_id_name=None):
    _forms = (f for f in forms if f.has_changed())
    for form in _forms:
        log.debug(f'form has changed : {form.changed_data}')

        # set id value to instead by mode_id
        if model_id_name:
            if hasattr(form.instance, model_id_name):
                form_id_name = form_id_name or model_id_name
                form.is_valid()  # make sure cleaned_data exist
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

    res_formset = create_formset(LocationResourceForm, post_data=request.POST,
                                 prefix='loc_res', many_related_manager=loc.resources)
    comment_formset = create_formset(LocationCommentForm, post_data=request.POST,
                                     prefix='loc_comment', many_related_manager=loc.comments)
    images_formset = create_formset(LocationImageForm, post_data=request.POST,
                                    prefix='loc_image', many_related_manager=loc.images)
    img_form = LocUploadImageForm(request.POST or None, request.FILES)

    def _render_full_form():

        # reversed list for UI
        for fs in [res_formset, images_formset, comment_formset]:
            fs.forms = list(reversed(fs.forms))

        return render(request, 'location/full_form.html',
                      {'loc_form': loc_form,
                       'res_formset': res_formset,
                       'comment_formset': comment_formset,
                       'images_formset': images_formset,
                       'loc_id': location_id,
                       'img_form': img_form,
                       'total_images': loc.images.count(),
                       })

    if request.method == 'POST':
        form_formsets = [loc_form, res_formset, comment_formset, images_formset, img_form]

        if not all(f.is_valid() for f in form_formsets):
            log.warning(f'something invalid')
            return _render_full_form()

        update_current_user_timestamp(request.user.username, form_formsets)

        # save formset
        save_formset(res_formset, loc.resources, model_id_name='resource_id')
        save_formset(comment_formset, loc.comments, model_id_name='comment_id')
        images_formset = (f for f in images_formset if f.is_valid())
        images_formset = (f for f in images_formset if f.cleaned_data.get('image_filename'))
        save_formset(images_formset, loc.images, model_id_name='image_id')

        # save if user uploaded an image
        if uploaded_img_file := img_form.cleaned_data.get('image'):
            file_path = media_service.save_uploaded_img(uploaded_img_file)
            file_url = media_service.get_img_url_by_file_path(file_path)
            img_obj = CofkUnionImage(image_filename=file_url, display_order=0,
                                     licence_details='', credits='',
                                     licence_url=settings.DEFAULT_IMG_LICENCE_URL)
            img_obj.update_current_user_timestamp(request.user.username)
            img_obj.save()
            loc.images.add(img_obj)

        loc_form.save()
        log.info(f'location [{location_id}] have been saved')
        return redirect('location:search')

    return _render_full_form()


class LocationMergeView(ListView):
    template_name = 'location/merge.html'

    @property
    def request_data(self):
        """ by default requests data would be GET  """
        return self.request.GET

    def get_queryset(self):
        # KTODO
        return []

    def get(self, request, *args, **kwargs):
        # response for search query
        print(self.request_data)
        return super().get(request, *args, **kwargs)


class LocationSearchView(BasicSearchView):
    paginate_by = 4

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request_data)]

    @property
    def sort_by_choices(self) -> List[Tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
            ('-location_name', 'Location Name desc',),
            ('location_name', 'Location Name asc',),
        ]

    def get_queryset(self):
        queryset = CofkUnionLocation.objects.all()

        # queries for like_fields
        field_fn_maps = {
            'editors_notes': model_utils.create_contains_query,
            'location_name': model_utils.create_contains_query,
            'location_id': model_utils.create_eq_query,
            'latitude': model_utils.create_contains_query,
            'longitude': model_utils.create_contains_query,
            'element_1_eg_room': model_utils.create_contains_query,
            'element_2_eg_building': model_utils.create_contains_query,
            'element_3_eg_parish': model_utils.create_contains_query,
            'element_4_eg_city': model_utils.create_contains_query,
            'element_5_eg_county': model_utils.create_contains_query,
            'element_6_eg_country': model_utils.create_contains_query,
            'element_7_eg_empire': model_utils.create_contains_query,
        }

        query_field_values = ((f, self.request_data.get(f)) for f in field_fn_maps.keys())
        query_field_values = ((f, v) for f, v in query_field_values if v)
        queries = [field_fn_maps[f](f, v) for f, v in query_field_values]

        if queries:
            queryset = queryset.filter(model_utils.any_queries(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def title(self) -> str:
        return 'Location'

    @property
    def merge_page_name(self):
        return 'location:merge'

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return LocationCompactSearchResultsRenderer

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return LocationTableSearchResultsRenderer

    @property
    def download_csv_handler(self) -> DownloadCsvHandler:
        return LocationDownloadCsvHandler()


class LocationDownloadCsvHandler(DownloadCsvHandler):
    def get_header_list(self) -> list[str]:
        return [
            "Location name",
            "Location id",
            "Editors notes",
            "Sent",
            "Recd",
            "All works",
            "Researchers notes",
            "Related resources",
            "Latitude",
            "Longitude",
            "Element 1 eg room"
            "Element 2 eg building"
            "Element 3 eg parish"
            "Element 4 eg city"
            "Element 5 eg county"
            "Element 6 eg country"
            "Element 7 eg empire"
            "Images",
            "Change user",
            "Change timestamp",
        ]

    def obj_to_values(self, obj) -> Iterable[str]:
        obj: CofkUnionLocation
        values = (
            obj.location_name,
            obj.location_id,
            obj.editors_notes,
            '0',  # KTODO send value
            '0',  # KTODO recd value
            '0',  # KTODO All works, should be send + recd
            ' ~ '.join(r.comment for r in obj.comments.iterator()),
            ' ~ '.join(r.resource_url for r in obj.resources.iterator()),
            obj.latitude,
            obj.longitude,
            obj.element_1_eg_room,
            obj.element_2_eg_building,
            obj.element_3_eg_parish,
            obj.element_4_eg_city,
            obj.element_5_eg_county,
            obj.element_6_eg_country,
            obj.element_7_eg_empire,
            ' ~ '.join(r.image_filename for r in obj.images.iterator()),
            obj.change_timestamp,
            obj.change_user,
        )
        values = map(str, values)
        return values
