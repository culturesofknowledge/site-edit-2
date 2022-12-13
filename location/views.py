import itertools
import logging
from typing import Iterable, Union, Type, Callable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseForm, BaseFormSet
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from core.constant import REL_TYPE_COMMENT_REFERS_TO
from core.forms import CommentForm
from core.helper import view_utils, renderer_utils, query_utils, download_csv_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.recref_handler import RecrefFormsetHandler, ImageRecrefHandler, TargetResourceFormsetHandler
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_handler import FullFormHandler
from core.helper.view_utils import BasicSearchView, CommonInitFormViewTemplate
from core.models import Recref
from location import location_utils
from location.forms import LocationForm, GeneralSearchFieldset
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap, CofkLocationImageMap
from location.recref_adapter import LocationCommentRecrefAdapter, LocationResourceRecrefAdapter, \
    LocationImageRecrefAdapter
from location.view_components import LocationFormDescriptor

log = logging.getLogger(__name__)
FormOrFormSet = Union[BaseForm, BaseFormSet]


class LocationInitView(LoginRequiredMixin, CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'location/init_form.html', {'loc_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('location:full_form', new_instance.location_id)

    @property
    def form_factory(self) -> Callable[..., BaseForm]:
        return LocationForm


class LocationQuickInitView(LocationInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('location:return_quick_init', new_instance.location_id)


@login_required
def return_quick_init(request, pk):
    location: CofkUnionLocation = CofkUnionLocation.objects.get(location_id=pk)
    return view_utils.render_return_quick_init(
        request, 'Place',
        location_utils.get_recref_display_name(location),
        location_utils.get_recref_target_id(location),
    )


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


def save_changed_forms(form_formsets: Iterable[FormOrFormSet]):
    for f in flat_changed_forms(form_formsets):
        f.save()


class LocationFFH(FullFormHandler):

    def load_data(self, pk, *args, request_data=None, request=None, **kwargs):
        self.loc = None
        self.location_id = pk or request.POST.get('location_id')
        if self.location_id:
            self.loc = get_object_or_404(CofkUnionLocation, pk=self.location_id)

        self.loc_form = LocationForm(request_data, instance=self.loc)

        self.add_recref_formset_handler(
            LocationResourceFormsetHandler(request_data=request_data,
                                           parent=self.loc)
        )
        self.add_recref_formset_handler(LocationCommentFormsetHandler(prefix='comment',
                                                                      request_data=request_data,
                                                                      form=CommentForm,
                                                                      rel_type=REL_TYPE_COMMENT_REFERS_TO,
                                                                      parent=self.loc))

        self.img_recref_handler = LocationImageRecrefHandler(request_data, request and request.FILES,
                                                             parent=self.loc)

    def create_context(self):
        context = super().create_context()
        context.update(
            {
                'loc_id': self.location_id,
            } | LocationFormDescriptor(self.loc).create_context()
        )
        return context

    def render_form(self, request):
        return render(request, 'location/full_form.html', self.create_context())


@login_required
def full_form(request, location_id):
    fhandler = LocationFFH(location_id, request_data=request.POST, request=request)

    if request.method == 'POST':

        if fhandler.is_invalid():
            return fhandler.render_form(request)

        # save formset
        fhandler.loc_form.save()
        fhandler.save_all_recref_formset(fhandler.loc_form.instance, request)

        log.info(f'location [{location_id}] have been saved')
        fhandler.load_data(location_id, request_data=None)

    return fhandler.render_form(request)


class LocationMergeView(LoginRequiredMixin, ListView):
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


class LocationSearchView(LoginRequiredMixin, BasicSearchView):

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request_data)]

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('location_name', 'Location name(s)',),
            ('location_id', 'Location ID',),
            ('editors_notes', 'Editors\' notes',),
            ('sent', 'Sent',),
            ('recd', 'Rec\'d',),
            ('all_works', 'Sent or Rec\'d',),
            ('researchers_notes', 'Researchers\' notes',),
            ('related_resources', 'Related resources',),
            ('latitude', 'Latitude',),
            ('longitude', 'Longitude',),
            ('element_1_eg_room', '1. E.g.room',),
            ('element_2_eg_building', '2. E.g.building',),
            ('element_3_eg_parish', '3. E.g.district of city',),
            ('element_4_eg_city', '4. E.g.city',),
            ('element_5_eg_county', '5. E.g.county',),
            ('element_6_eg_country', '6. E.g.country',),
            ('element_7_eg_empire', '7. E.g.empire',),
            ('images', 'Images',),
            ('change_user', 'Last changed by',),
            ('change_timestamp', 'Last edit',),
        ]

    def get_queryset(self):
        # queries for like_fields
        field_fn_maps = {
            'editors_notes': query_utils.create_contains_query,
            'location_name': query_utils.create_contains_query,
            'location_id': query_utils.create_eq_query,
            'latitude': query_utils.create_contains_query,
            'longitude': query_utils.create_contains_query,
            'element_1_eg_room': query_utils.create_contains_query,
            'element_2_eg_building': query_utils.create_contains_query,
            'element_3_eg_parish': query_utils.create_contains_query,
            'element_4_eg_city': query_utils.create_contains_query,
            'element_5_eg_county': query_utils.create_contains_query,
            'element_6_eg_country': query_utils.create_contains_query,
            'element_7_eg_empire': query_utils.create_contains_query,
        }

        # KTODO support lookup query_utils.create_queries_by_lookup_field

        queries = query_utils.create_queries_by_field_fn_maps(field_fn_maps, self.request_data)

        return self.create_queryset_by_queries(CofkUnionLocation, queries)

    @property
    def entity(self) -> str:
        return 'location,locations'

    @property
    def merge_page_vname(self) -> str:
        return 'location:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'location:return_quick_init'

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return renderer_utils.create_compact_renderer(item_template_name='location/compact_item.html')

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer(
            'location/search_table_layout.html'
        )

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
            download_csv_utils.join_comment_lines(obj.comments.iterator()),
            download_csv_utils.join_resource_lines(obj.resources.iterator()),
            obj.latitude,
            obj.longitude,
            obj.element_1_eg_room,
            obj.element_2_eg_building,
            obj.element_3_eg_parish,
            obj.element_4_eg_city,
            obj.element_5_eg_county,
            obj.element_6_eg_country,
            obj.element_7_eg_empire,
            download_csv_utils.join_image_lines(obj.images.iterator()),
            obj.change_timestamp,
            obj.change_user,
        )
        return values


class LocationCommentFormsetHandler(RecrefFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return LocationCommentRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkLocationCommentMap.objects.filter(location=parent, comment=target).first()


class LocationResourceFormsetHandler(TargetResourceFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return LocationResourceRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkLocationResourceMap.objects.filter(location=parent, resource=target).first()


class LocationImageRecrefHandler(ImageRecrefHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return LocationImageRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkLocationImageMap.objects.filter(location=parent, image=target).first()
