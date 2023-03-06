import itertools
import logging
from typing import Iterable, Union, Type, Callable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Count, Q
from django.forms import BaseForm, BaseFormSet
from django.shortcuts import render, get_object_or_404, redirect

from core.constant import REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM
from core.forms import CommentForm
from core.helper import view_utils, renderer_utils, query_utils, download_csv_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.date_utils import str_to_std_datetime
from core.helper.model_utils import ModelLike
from core.helper.recref_handler import RecrefFormsetHandler, ImageRecrefHandler, TargetResourceFormsetHandler
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler
from core.helper.view_handler import FullFormHandler
from core.helper.view_utils import BasicSearchView, CommonInitFormViewTemplate, MergeChoiceViews, MergeChoiceContext, \
    MergeActionViews, MergeConfirmViews
from core.models import Recref
from location import location_utils
from location.forms import LocationForm, GeneralSearchFieldset, field_label_map
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


class LocationMergeChoiceView(LoginRequiredMixin, MergeChoiceViews):
    @staticmethod
    def get_id_field():
        return CofkUnionLocation.location_id

    def to_context_list(self, merge_id_list: list[str]) -> Iterable['MergeChoiceContext']:
        return self.create_merge_choice_context_by_id_field(self.get_id_field(), merge_id_list)


class LocationMergeConfirmView(LoginRequiredMixin, MergeConfirmViews):
    @property
    def target_model_class(self) -> Type[ModelLike]:
        return CofkUnionLocation


class LocationMergeActionView(LoginRequiredMixin, MergeActionViews):
    @staticmethod
    def get_id_field():
        return LocationMergeChoiceView.get_id_field()

    @property
    def target_model_class(self) -> Type[ModelLike]:
        return CofkUnionLocation


class LocationSearchView(LoginRequiredMixin, BasicSearchView):

    @property
    def search_fields(self) -> list[str]:
        return ['location_name', 'editors_notes', 'location_id', 'researchers_notes', 'resources', 'latitude',
                'sent', 'recd', 'all_works', 'longitude', 'element_1_eg_room', 'element_2_eg_building',
                'element_3_eg_parish', 'element_4_eg_city', 'element_5_eg_county', 'element_6_eg_country',
                'element_7_eg_empire', 'images', 'change_user']

    @property
    def search_field_label_map(self) -> dict:
        return field_label_map

    @property
    def search_field_fn_maps(self) -> dict:
        return query_utils.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                   'change_timestamp', str_to_std_datetime)

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request_data)]

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('location_name', 'Location name',),
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

    def create_queryset_by_queries(self, model_class: Type[models.Model], queries: Iterable[Q]):
        queryset = model_class.objects.all()
        annotate = {'sent': Count('works', filter=Q(cofkworklocationmap__relationship_type=REL_TYPE_WAS_SENT_FROM)),
                    'recd': Count('works', filter=Q(cofkworklocationmap__relationship_type=REL_TYPE_WAS_SENT_TO)),
                    }
        annotate['all_works'] = annotate['sent'] + annotate['recd']

        queryset = queryset.annotate(**annotate)

        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_queryset(self):
        return self.get_queryset_by_request_data(self.request_data)

    def get_queryset_by_request_data(self, request_data) -> Iterable:
        search_fields_maps = {'location_name': ['location_name', 'location_synonyms'],
                              'resources': ['resources__resource_name', 'resources__resource_details',
                                            'resources__resource_url'],
                              'researchers_notes': ['comments__comment'],
                              'images': ['images__image_filename']}

        queries = query_utils.create_queries_by_field_fn_maps(self.search_field_fn_maps, request_data)
        queries.extend(
            query_utils.create_queries_by_lookup_field(request_data, self.search_fields, search_fields_maps)
        )

        return self.create_queryset_by_queries(CofkUnionLocation, queries).distinct()

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
