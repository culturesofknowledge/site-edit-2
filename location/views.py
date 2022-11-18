import itertools
import logging
from typing import Iterable, Union, Type, Callable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseForm, BaseFormSet, ModelForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from core.constant import REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_IS_RELATED_TO
from core.forms import CommentForm, ResourceForm
from core.helper import view_utils, renderer_utils, query_utils, download_csv_utils
from core.helper.common_recref_adapter import RecrefFormAdapter, TargetCommentRecrefAdapter, TargetResourceRecrefAdapter
from core.helper.model_utils import RecordTracker
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_utils import BasicSearchView, CommonInitFormViewTemplate, ImageHandler, RecrefFormsetHandler
from core.models import Recref
from location import location_utils
from location.forms import LocationForm, GeneralSearchFieldset
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap

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


def update_current_user_timestamp(user, form_formsets: Iterable[FormOrFormSet]):
    forms = flat_changed_forms(form_formsets)
    forms = (f for f in forms if isinstance(f, ModelForm))
    records = (f.instance for f in forms if isinstance(f.instance, RecordTracker))
    for r in records:
        r.update_current_user_timestamp(user)


def save_changed_forms(form_formsets: Iterable[FormOrFormSet]):
    for f in flat_changed_forms(form_formsets):
        f.save()


@login_required
def full_form(request, location_id):
    loc = None
    location_id = location_id or request.POST.get('location_id')
    if location_id:
        loc = get_object_or_404(CofkUnionLocation, pk=location_id)

    loc_form = LocationForm(request.POST or None, instance=loc)

    res_handler = LocationResourceFormsetHandler(prefix='res',
                                                 request_data=request.POST or None,
                                                 form=ResourceForm,
                                                 rel_type=REL_TYPE_IS_RELATED_TO,
                                                 parent=loc)
    comment_handler = LocationCommentFormsetHandler(prefix='comment',
                                                    request_data=request.POST or None,
                                                    form=CommentForm,
                                                    rel_type=REL_TYPE_COMMENT_REFERS_TO,
                                                    parent=loc)

    img_handler = ImageHandler(request.POST, request.FILES, loc.images)

    def _render_full_form():

        return render(request, 'location/full_form.html',
                      {'loc_form': loc_form,
                       res_handler.context_name: res_handler.formset,
                       comment_handler.context_name: comment_handler.formset,
                       'loc_id': location_id,
                       } | img_handler.create_context()
                      )

    if request.method == 'POST':
        form_formsets = [loc_form, res_handler.formset, comment_handler.formset, img_handler.image_formset,
                         img_handler.img_form]

        if view_utils.any_invalid_with_log(form_formsets):
            log.warning(f'something invalid')
            return _render_full_form()

        update_current_user_timestamp(request.user.username, form_formsets)

        # save formset
        res_handler.save(loc, request)
        comment_handler.save(loc, request)
        img_handler.save(request)

        loc_form.save()
        log.info(f'location [{location_id}] have been saved')
        return redirect('location:search')

    return _render_full_form()


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
        queryset = CofkUnionLocation.objects.all()

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

        queries = query_utils.create_queries_by_field_fn_maps(field_fn_maps, self.request_data)
        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

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


class LocationCommentRecrefAdapter(TargetCommentRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def recref_class(self) -> Type[Recref]:
        return CofkLocationCommentMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkLocationCommentMap
        recref.location = parent
        recref.comment = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationcommentmap_set, rel_type)


class LocationResourceFormsetHandler(RecrefFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return LocationResourceRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return CofkLocationResourceMap.objects.filter(location=parent, resource=target).first()


class LocationResourceRecrefAdapter(TargetResourceRecrefAdapter):
    def __init__(self, parent):
        self.parent: CofkUnionLocation = parent

    def recref_class(self) -> Type[Recref]:
        return CofkLocationResourceMap

    def set_parent_target_instance(self, recref, parent, target):
        recref: CofkLocationResourceMap
        recref.location = parent
        recref.resource = target

    def find_recref_records(self, rel_type):
        return self.find_recref_records_by_related_manger(self.parent.cofklocationresourcemap_set, rel_type)
