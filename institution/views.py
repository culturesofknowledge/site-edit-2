import logging
from abc import ABC
from typing import Callable, Iterable, Type, TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Lookup
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404

from clonefinder.features.dataset import inst_features
from clonefinder.services import clonefinder_schedule
from core import constant
from core.export_data import cell_values, download_csv_serv
from core.helper import renderer_serv, query_serv, view_serv, perm_serv
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.model_serv import ModelLike
from core.helper.recref_handler import ImageRecrefHandler, TargetResourceFormsetHandler
from core.helper.renderer_serv import RendererFactory
from core.helper.view_components import HeaderValues, DownloadCsvHandler
from core.helper.view_serv import CommonInitFormViewTemplate, DefaultSearchView, MergeChoiceViews, MergeActionViews, \
    MergeConfirmViews, ClonefinderSetting
from core.models import Recref, MergeHistory
from institution import inst_serv, models
from institution.forms import InstitutionForm, GeneralSearchFieldset
from institution.models import CofkUnionInstitution
from institution.recref_adapter import InstResourceRecrefAdapter, InstImageRecrefAdapter
from institution.view_components import InstFormDescriptor

if TYPE_CHECKING:
    from core.helper.view_serv import MergeChoiceContext

log = logging.getLogger(__name__)


class InstSearchView(LoginRequiredMixin, DefaultSearchView, ABC):

    @property
    def search_field_fn_maps(self) -> dict[str, Lookup]:
        return {
            'tombstone': view_serv.create_tombstone_query,
        } | query_serv.create_from_to_datetime('change_timestamp_from',
                                               'change_timestamp_to',
                                               'change_timestamp')

    @property
    def entity(self) -> str:
        return 'repository,repositories'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('institution_name', 'Repository name',),
            ('institution_synonyms', 'Alternative repository names',),
            ('institution_city', 'City name',),
            ('institution_city_synonyms', 'Alternative city names',),
            ('institution_country', 'Country name',),
            ('institution_country_synonyms', 'Alternative country names',),
            ('resources', 'Related resources',),
            ('editors_notes', 'Editors\' notes',),
            ('images', 'Images',),
            ('change_timestamp', 'Change timestamp',),
            ('change_user', 'Change user',),
            ('institution_id', 'Repository ID',),
        ]

    @property
    def search_field_combines(self) -> dict[str: list[str]]:
        return {
            'institution_name': ['institution_name', 'institution_synonyms'],
            'institution_city': ['institution_city', 'institution_city_synonyms'],
            'institution_country': ['institution_country', 'institution_country_synonyms'],
            'resources': ['resources__resource_name', 'resources__resource_details',
                          'resources__resource_url'],
            'images': ['images__image_filename']}

    @property
    def merge_page_vname(self) -> str:
        return 'institution:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'institution:return_quick_init'

    @property
    def default_order(self) -> str:
        return 'asc'

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionInstitution.objects.none()

        return self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

    def get_queryset_by_request_data(self, request_data, sort_by=None) -> Iterable:
        # queries for like_fields
        queries = query_serv.create_queries_by_field_fn_maps(request_data, self.search_field_fn_maps)

        queries.extend(
            query_serv.create_queries_by_lookup_field(request_data, self.search_fields, self.search_field_combines)
        )
        return self.create_queryset_by_queries(CofkUnionInstitution, queries, sort_by=sort_by).distinct()

    @property
    def compact_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_compact_renderer(item_template_name='institution/compact_item.html')

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer('institution/search_table_layout.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        default_values = {
            'tombstone': 'live',
        }
        data = default_values | self.request_data.dict()
        return [GeneralSearchFieldset(data)]

    @property
    def csv_export_setting(self):
        if not self.has_perms(constant.PM_EXPORT_FILE_INST):
            return None
        return (lambda: view_serv.create_export_file_name('inst', 'csv'),
                lambda: DownloadCsvHandler(InstCsvHeaderValues()).create_csv_file,
                constant.PM_EXPORT_FILE_INST)

    @property
    def clonefinder_setting(self) -> ClonefinderSetting | None:
        if not self.has_perms(constant.PM_CLONEFINDER_INST):
            return None

        def queryset_modifier(queryset):
            return queryset.values(*inst_features.REQUIRED_FIELDS)

        return ClonefinderSetting(
            model_name=CofkUnionInstitution.__name__,
            queryset_modifier=queryset_modifier,
            status_handler=clonefinder_schedule.inst_status_handler,
            permissions=[constant.PM_CLONEFINDER_INST],
        )


class InstInitView(PermissionRequiredMixin, LoginRequiredMixin, CommonInitFormViewTemplate):
    permission_required = constant.PM_CHANGE_INST

    def resp_form_page(self, request, form):
        return render(request, 'institution/init_form.html', {'inst_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('institution:full_form', new_instance.institution_id)

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        return InstitutionForm


@login_required
def full_form(request, pk):
    inst: CofkUnionInstitution = get_object_or_404(CofkUnionInstitution, pk=pk)
    inst_form = InstitutionForm(request.POST or None, instance=inst)

    res_handler = InstResourceFormsetHandler(request_data=request.POST or None,
                                             parent=inst)

    img_recref_handler = InstImageRecrefHandler(request.POST or None, request.FILES, parent=inst)

    def _render_form():
        return render(request, 'institution/init_form.html',
                      ({
                           'inst_form': inst_form,
                       }
                       | img_recref_handler.create_context()
                       | res_handler.create_context()
                       | InstFormDescriptor(inst).create_context()
                       | view_serv.create_is_save_success_context(is_save_success)
                       | {
                           'merge_histories': MergeHistory.objects.get_by_new_model(inst),
                       }
                       ))

    is_save_success = False
    if request.POST:
        perm_serv.validate_permission_denied(request.user, constant.PM_CHANGE_INST)

        if view_serv.any_invalid_with_log([
            inst_form,
            res_handler.formset,
            img_recref_handler.formset, img_recref_handler.upload_img_form,
        ]):
            return _render_form()

        res_handler.save(inst, request)
        img_recref_handler.save(inst, request)

        inst.update_current_user_timestamp(request.user.username)
        inst_form.save()
        is_save_success = view_serv.mark_callback_save_success(request)

    return _render_form()


class InstQuickInitView(InstInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('institution:return_quick_init', new_instance.pk)


@login_required
def return_quick_init(request, pk):
    inst: CofkUnionInstitution = CofkUnionInstitution.objects.get(institution_id=pk)
    return view_serv.render_return_quick_init(
        request, 'Repositories',
        inst_serv.get_recref_display_name(inst),
        inst_serv.get_recref_target_id(inst),
    )


class InstResourceFormsetHandler(TargetResourceFormsetHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return InstResourceRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return models.CofkInstitutionResourceMap.objects.filter(institution=parent, resource=target).first()


class InstImageRecrefHandler(ImageRecrefHandler):
    def create_recref_adapter(self, parent) -> RecrefFormAdapter:
        return InstImageRecrefAdapter(parent)

    def find_org_recref_fn(self, parent, target) -> Recref | None:
        return models.CofkInstitutionImageMap.objects.filter(institution=parent, image=target).first()


class InstMergeChoiceView(LoginRequiredMixin, MergeChoiceViews):
    @staticmethod
    def get_id_field():
        return CofkUnionInstitution.institution_id

    def to_context_list(self, merge_id_list: list[str]) -> Iterable['MergeChoiceContext']:
        return self.create_merge_choice_context_by_id_field(self.get_id_field(), merge_id_list)


class InstMergeConfirmView(LoginRequiredMixin, MergeConfirmViews):
    @property
    def target_model_class(self) -> Type[ModelLike]:
        return CofkUnionInstitution


class InstMergeActionView(LoginRequiredMixin, MergeActionViews):

    @staticmethod
    def get_id_field():
        return InstMergeChoiceView.get_id_field()

    @property
    def target_model_class(self) -> Type[ModelLike]:
        return CofkUnionInstitution


class InstCsvHeaderValues(HeaderValues):
    def get_header_list(self) -> list[str]:
        return [
            "Repository ID",
            "Institution name",
            "Alternative institution  names",
            "City name",
            "Alternative city  names",
            "Country name",
            "Alternative country  names",
            "Related resources",
            "Editors' notes",
            "Images",
            "Change timestamp",
            "Change user"
        ]

    def obj_to_values(self, obj: CofkUnionInstitution) -> Iterable:
        return [
            obj.institution_id,
            obj.institution_name,
            obj.institution_synonyms,
            obj.institution_city,
            obj.institution_city_synonyms,
            obj.institution_country,
            obj.institution_country_synonyms,
            cell_values.resource_str_by_list(obj.resources.iterator()),
            obj.editors_notes,
            download_csv_serv.join_image_lines(obj.images.iterator()),
            cell_values.simple_datetime(obj.change_timestamp),
            obj.change_user,
        ]
