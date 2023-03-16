import logging
from abc import ABC
from typing import Callable, Iterable, Type, TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404

from core.export_data import cell_values, download_csv_utils
from core.helper import renderer_utils, query_utils, view_utils
from core.helper.common_recref_adapter import RecrefFormAdapter
from core.helper.model_utils import ModelLike
from core.helper.recref_handler import ImageRecrefHandler, TargetResourceFormsetHandler
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_components import HeaderValues, DownloadCsvHandler
from core.helper.view_utils import CommonInitFormViewTemplate, DefaultSearchView, MergeChoiceViews, MergeActionViews, \
    MergeConfirmViews
from core.models import Recref
from institution import inst_utils, models
from institution.forms import InstitutionForm, GeneralSearchFieldset, field_label_map
from institution.models import CofkUnionInstitution
from institution.recref_adapter import InstResourceRecrefAdapter, InstImageRecrefAdapter
from institution.view_components import InstFormDescriptor

if TYPE_CHECKING:
    from core.helper.view_utils import MergeChoiceContext

log = logging.getLogger(__name__)


class InstSearchView(LoginRequiredMixin, DefaultSearchView, ABC):

    @property
    def search_fields(self) -> list[str]:
        return ['institution_name', 'editors_notes', 'institution_city', 'institution_country',
                'change_user', 'institution_id', 'resources', 'images']

    @property
    def search_field_fn_maps(self) -> dict:
        return query_utils.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                   'change_timestamp')

    @property
    def search_field_label_map(self) -> dict:
        """
        return
        """
        return field_label_map

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
    def merge_page_vname(self) -> str:
        return 'institution:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'institution:return_quick_init'

    def get_queryset(self):
        return self.get_queryset_by_request_data(self.request_data, sort_by=self.get_sort_by())

    def get_queryset_by_request_data(self, request_data, sort_by=None) -> Iterable:
        # queries for like_fields
        queries = query_utils.create_queries_by_field_fn_maps(self.search_field_fn_maps, request_data)

        search_fields_maps = {
            'institution_name': ['institution_name', 'institution_synonyms'],
            'institution_city': ['institution_city', 'institution_city_synonyms'],
            'institution_country': ['institution_country', 'institution_country_synonyms'],
            'resources': ['resources__resource_name', 'resources__resource_details',
                          'resources__resource_url'],
            'images': ['images__image_filename']}

        queries.extend(
            query_utils.create_queries_by_lookup_field(request_data, self.search_fields, search_fields_maps)
        )
        return self.create_queryset_by_queries(CofkUnionInstitution, queries, sort_by=sort_by).distinct()

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return renderer_utils.create_compact_renderer(item_template_name='institution/compact_item.html')

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('institution/search_table_layout.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request_data.dict())]

    @property
    def csv_export_setting(self):
        return (lambda: view_utils.create_export_file_name('inst', 'csv'),
                lambda: DownloadCsvHandler(InstCsvHeaderValues()).create_csv_file)


class InstInitView(LoginRequiredMixin, CommonInitFormViewTemplate):

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
                       )
                      )

    if request.POST:
        if view_utils.any_invalid_with_log([
            inst_form,
            res_handler.formset,
            img_recref_handler.formset, img_recref_handler.upload_img_form,
        ]):
            return _render_form()

        res_handler.save(inst, request)
        img_recref_handler.save(inst, request)

        inst.update_current_user_timestamp(request.user.username)
        inst_form.save()

    return _render_form()


class InstQuickInitView(InstInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('institution:return_quick_init', new_instance.pk)


@login_required
def return_quick_init(request, pk):
    inst: CofkUnionInstitution = CofkUnionInstitution.objects.get(institution_id=pk)
    return view_utils.render_return_quick_init(
        request, 'Repositories',
        inst_utils.get_recref_display_name(inst),
        inst_utils.get_recref_target_id(inst),
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
            download_csv_utils.join_image_lines(obj.images.iterator()),
            cell_values.simple_datetime(obj.change_timestamp),
            obj.change_user,
        ]
