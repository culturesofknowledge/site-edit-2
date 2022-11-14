from typing import Callable, Iterable, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404

from core.helper import renderer_utils, query_utils, view_utils
from core.helper.renderer_utils import CompactSearchResultsRenderer
from core.helper.view_utils import CommonInitFormViewTemplate, DefaultSearchView
from institution import inst_utils
from institution.forms import InstitutionForm, GeneralSearchFieldset
from institution.models import CofkUnionInstitution


class InstSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def entity(self) -> str:
        return 'institution,institutions'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('-change_timestamp', 'Change Timestamp desc',),
            ('change_timestamp', 'Change Timestamp asc',),
        ]

    @property
    def merge_page_vname(self) -> str:
        return 'institution:merge'

    @property
    def return_quick_init_vname(self) -> str:
        return 'institution:return_quick_init'

    def get_queryset(self):
        # KTODO
        queryset = CofkUnionInstitution.objects.all()

        # queries for like_fields
        field_fn_maps = {
            'institution_id': query_utils.create_eq_query,
        }

        queries = query_utils.create_queries_by_field_fn_maps(field_fn_maps, self.request_data)

        if queries:
            queryset = queryset.filter(query_utils.all_queries_match(queries))

        if sort_by := self.get_sort_by():
            queryset = queryset.order_by(sort_by)
        return queryset

    @property
    def compact_search_results_renderer_factory(self) -> Type[CompactSearchResultsRenderer]:
        return renderer_utils.create_compact_renderer(item_template_name='institution/compact_item.html')

    @property
    def table_search_results_renderer_factory(self) -> Callable[[Iterable], Callable]:
        return renderer_utils.create_table_search_results_renderer('institution/search_table_layout.html')

    @property
    def query_fieldset_list(self) -> Iterable:
        default_values = {
            'foaf_name_lookup': 'starts_with',
        }
        request_data = default_values | self.request_data.dict()

        return [GeneralSearchFieldset(request_data)]


class InstInitView(LoginRequiredMixin, CommonInitFormViewTemplate):

    def resp_form_page(self, request, form):
        return render(request, 'institution/init_form.html', {'inst_form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('institution:search')

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        return InstitutionForm


@login_required
def full_form(request, pk):
    # KTODO
    inst = get_object_or_404(CofkUnionInstitution, pk=pk)
    inst_form = InstitutionForm(request.POST or None, instance=inst)

    def _render_form():
        return render(request, 'institution/init_form.html', {
            'inst_form': inst_form,
        })

    if request.POST:
        if not inst_form.is_valid():
            return _render_form()

        inst_form.save()
        return redirect('institution:search')

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
