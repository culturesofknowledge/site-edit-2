import itertools
import logging
from typing import Iterable, Union, Type, Callable, List

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import models
from django.db.models import Q
from django.forms import BaseForm, BaseFormSet
from django.shortcuts import render, get_object_or_404, redirect

from core import constant
from core.constant import REL_TYPE_COMMENT_REFERS_TO, REL_TYPE_WAS_SENT_TO, REL_TYPE_WAS_SENT_FROM
from core.export_data import download_csv_utils, cell_values
from core.forms import CommentForm
from core.helper import view_utils, renderer_utils, query_utils, perm_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.model_utils import ModelLike
from core.helper.recref_handler import RecrefFormsetHandler, ImageRecrefHandler, TargetResourceFormsetHandler
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import DownloadCsvHandler, HeaderValues
from core.helper.view_handler import FullFormHandler
from core.helper.view_utils import BasicSearchView, CommonInitFormViewTemplate, MergeChoiceViews, MergeChoiceContext, \
    MergeActionViews, MergeConfirmViews, DeleteConfirmView
from core.models import Recref
from location import location_utils
from location.forms import LocationForm, GeneralSearchFieldset
from location.models import CofkUnionLocation, CofkLocationCommentMap, CofkLocationResourceMap, CofkLocationImageMap, \
    create_sql_count_work_by_location
from location.recref_adapter import LocationCommentRecrefAdapter, LocationResourceRecrefAdapter, \
    LocationImageRecrefAdapter
from location.view_components import LocationFormDescriptor

log = logging.getLogger(__name__)
FormOrFormSet = Union[BaseForm, BaseFormSet]


def create_queryset_by_queries(model_class: Type[models.Model], queries: Iterable[Q],
                               sort_by=None):
    queryset = model_class.objects
    annotate = {
        'sent': create_sql_count_work_by_location([REL_TYPE_WAS_SENT_FROM]),
        'recd': create_sql_count_work_by_location([REL_TYPE_WAS_SENT_TO]),
        'all_works': create_sql_count_work_by_location([REL_TYPE_WAS_SENT_FROM, REL_TYPE_WAS_SENT_TO]),
    }

    queryset = query_utils.update_queryset(queryset, model_class, queries, annotate=annotate,
                                           sort_by=sort_by)
    return queryset


class LocationInitView(PermissionRequiredMixin, LoginRequiredMixin, CommonInitFormViewTemplate):
    permission_required = constant.PM_CHANGE_LOCATION

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
        self.loc: CofkUnionLocation | None = None
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

    def create_context(self, is_save_success=False):
        context = super().create_context()
        context.update(
            {
                'loc_id': self.location_id,
            } | LocationFormDescriptor(self.loc).create_context()
            | view_utils.create_is_save_success_context(is_save_success)
        )
        return context

    def render_form(self, request, is_save_success=False):
        return render(request, 'location/full_form.html', self.create_context(is_save_success=is_save_success))


@login_required
def full_form(request, location_id):
    fhandler = LocationFFH(location_id, request_data=request.POST, request=request)

    is_save_success = False
    if request.method == 'POST':
        perm_utils.validate_permission_denied(request.user, constant.PM_CHANGE_LOCATION)

        if fhandler.is_invalid():
            return fhandler.render_form(request)

        # save formset
        fhandler.loc.update_current_user_timestamp(request.user.username)
        fhandler.loc_form.save()
        fhandler.save_all_recref_formset(fhandler.loc_form.instance, request)
        fhandler.img_recref_handler.save(fhandler.loc_form.instance, request)

        log.info(f'location [{location_id}] have been saved')
        fhandler.load_data(location_id, request_data=None)
        is_save_success = view_utils.mark_callback_save_success(request)

    return fhandler.render_form(request, is_save_success=is_save_success)


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
    def search_field_combines(self) -> dict[str: List[str]]:
        return {'location_name': ['location_name', 'location_synonyms'],
                'resources': ['resources__resource_name', 'resources__resource_details',
                              'resources__resource_url'],
                'researchers_notes': ['comments__comment'],
                'images': ['images__image_filename']}

    @property
    def search_field_fn_maps(self) -> dict:
        return query_utils.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                   'change_timestamp')

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

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionLocation.objects.none()

        return self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

    def get_queryset_by_request_data(self, request_data, sort_by=None) -> Iterable:
        search_fields_maps = {'location_name': ['location_name', 'location_synonyms'],
                              'resources': ['resources__resource_name', 'resources__resource_details',
                                            'resources__resource_url'],
                              'researchers_notes': ['comments__comment'],
                              'images': ['images__image_filename']}

        queries = query_utils.create_queries_by_field_fn_maps(self.search_field_fn_maps, request_data)
        queries.extend(
            query_utils.create_queries_by_lookup_field(request_data, self.search_fields, search_fields_maps)
        )

        return create_queryset_by_queries(CofkUnionLocation, queries, sort_by=sort_by)

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
    def csv_export_setting(self):
        if not self.has_perms(constant.PM_EXPORT_FILE_LOCATION):
            return None
        return (lambda: view_utils.create_export_file_name('location', 'csv'),
                lambda: DownloadCsvHandler(LocationCsvHeaderValues()).create_csv_file,
                constant.PM_EXPORT_FILE_LOCATION,)


class LocationCsvHeaderValues(HeaderValues):
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
            "Element 1 eg room",
            "Element 2 eg building",
            "Element 3 eg parish",
            "Element 4 eg city",
            "Element 5 eg county",
            "Element 6 eg country",
            "Element 7 eg empire",
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
            obj.sent,
            obj.recd,
            obj.all_works,
            download_csv_utils.join_comment_lines(obj.comments.iterator()),
            cell_values.resource_str_by_list(obj.resources.iterator()),
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
            obj.change_user,
            cell_values.simple_datetime(obj.change_timestamp),
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


class LocationDeleteConfirmView(DeleteConfirmView):
    def get_model_class(self) -> Type[ModelLike]:
        return CofkUnionLocation

    def get_obj_desc_list(self, obj: CofkUnionLocation) -> list[str]:
        desc_list = [
            obj.location_name,
            obj.location_synonyms,
            obj.latitude,
            obj.longitude,
        ]
        desc_list = filter(None, desc_list)
        desc_list = list(desc_list)
        return desc_list
