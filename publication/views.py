from typing import Callable, Iterable, Type

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Lookup
from django.forms import ModelForm
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render

from core import constant
from core.helper import renderer_serv, query_serv, view_serv, perm_serv
from core.helper.model_serv import ModelLike
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import CommonInitFormViewTemplate, DefaultSearchView, DeleteConfirmView
from publication.forms import PublicationForm, GeneralSearchFieldset
from publication.models import CofkUnionPublication
from publication.publication_suggestion import PublicationSuggestion
from suggestions import views as sug_view


class PubSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def query_fieldset_list(self) -> Iterable:
        return [GeneralSearchFieldset(self.request_data)]

    @property
    def search_field_fn_maps(self) -> dict[str, Lookup]:
        return query_serv.create_from_to_datetime('change_timestamp_from', 'change_timestamp_to',
                                                   'change_timestamp')

    @property
    def entity(self) -> str:
        return 'publication,publications'

    @property
    def default_order(self) -> str:
        return 'asc'

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('publication_details', 'Publication details',),
            ('abbrev', 'Abbreviation',),
            ('change_user', 'Last changed by',),
            ('change_timestamp', 'Change timestamp',),
            ('publication_id', 'Publication ID',),
        ]

    @property
    def return_quick_init_vname(self) -> str:
        return 'publication:return_quick_init'

    def get_queryset(self):
        if not self.request_data:
            return CofkUnionPublication.objects.none()

        # queries for like_fields
        queries = query_serv.create_queries_by_field_fn_maps(self.request_data, self.search_field_fn_maps)

        queries.extend(
            query_serv.create_queries_by_lookup_field(self.request_data, self.search_fields)
        )
        return self.create_queryset_by_queries(CofkUnionPublication, queries)

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer('publication/search_table_layout.html')


class PubInitView(PermissionRequiredMixin, LoginRequiredMixin, CommonInitFormViewTemplate):
    permission_required = constant.PM_CHANGE_PUBLICATION

    def resp_form_page(self, request, form):
        return render(request, 'publication/init_form.html', {'pub_form': form})

    def resp_after_saved(self, request, form, new_instance):
        suggestion_id = request.GET.get('from_suggestion', None)
        if suggestion_id:
            sug_view.save_with_related_info(suggestion_id, new_instance.publication_id)
        return redirect('publication:search')

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        return PublicationForm

    def get(self, request, *args, **kwargs):
        is_org_form = request and request.GET.get('publication_form_type') == 'org'
        initial = {}
        if is_org_form:
            initial['is_organisation'] = TRUE_CHAR
        if request and request.GET.get('from_suggestion', ''):
            from_suggestion = request.GET.get('from_suggestion')
            sug_values = PublicationSuggestion(from_suggestion).initial_form_values()
            if sug_values:
                initial.update(sug_values)
        form = self.form_factory(initial=initial)
        return self.resp_form_page(request, form)

@login_required
def full_form(request, pk):
    pub: CofkUnionPublication = get_object_or_404(CofkUnionPublication, pk=pk)
    pub_form = PublicationForm(request.POST or None, instance=pub)

    def _render_form():
        return render(request, 'publication/init_form.html',
                      {
                          'pub_form': pub_form,
                      } | view_serv.create_is_save_success_context(is_save_success)
                      )

    is_save_success = False
    if request.POST:
        perm_serv.validate_permission_denied(request.user, constant.PM_CHANGE_PUBLICATION)
        if not pub_form.is_valid():
            return _render_form()

        pub.update_current_user_timestamp(request.user.username)
        pub_form.save()
        is_save_success = view_serv.mark_callback_save_success(request)

    return _render_form()


class PubQuickInitView(PubInitView):
    def resp_after_saved(self, request, form, new_instance):
        return redirect('publication:return_quick_init', new_instance.pk)


@login_required
def return_quick_init(request, pk):
    pub = CofkUnionPublication.objects.get(pk=pk)
    return render(request, 'publication/return_quick_init_pub.html', {
        'pub': pub,
    })


class PubDeleteConfirmView(PermissionRequiredMixin, DeleteConfirmView):
    permission_required = constant.PM_CHANGE_PUBLICATION

    def get_model_class(self) -> Type[ModelLike]:
        return CofkUnionPublication

    def get_obj_desc_list(self, obj: CofkUnionPublication) -> list[str]:
        desc_list = [
            obj.publication_details,
            obj.abbrev,
        ]
        desc_list = filter(None, desc_list)
        desc_list = list(desc_list)
        return desc_list
