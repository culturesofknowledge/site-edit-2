from typing import Callable, Iterable

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db.models import Count
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.urls import reverse

from catalogue.forms import CatalogueSearchFieldset
from core import constant
from core.forms import CatalogueForm
from core.helper import renderer_serv, query_serv, perm_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView, CommonInitFormViewTemplate
from core.models import CofkLookupCatalogue
from login import utils


@login_required
@permission_required(constant.PM_CHANGE_LOOKUPCAT)
def update_catalogue(request, pk=None):
    instance: CofkLookupCatalogue = CofkLookupCatalogue.objects.filter(pk=pk).first()
    form = CatalogueForm(request.POST or None, instance=instance)
    template = 'catalogue/init_form.html'
    if 'delete' in request.POST:

        if instance and getattr(instance, 'work').count() == 0:
            msg = f'Successfully deleted catalogue' \
                  f' "{getattr(instance, 'catalogue_name')}" '
            instance.delete()
            messages.success(request, msg)
            return redirect('catalogue:search')
        else:
            messages.error(request, f'Cannot delete catalogue as works associated with it.')
            template = 'catalogue/update_form.html'

    elif 'save' in request.POST:
        # Update

        if instance:
            form = CatalogueForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()

            messages.success(request, f'Successfully updated catalogue'
                                      f' "{getattr(instance, 'catalogue_name')}" ')
        template = 'catalogue/update_form.html'

    elif instance:
        template = 'catalogue/update_form.html'

    elif 'add' in request.POST:

        # Create new list object
        if form.is_valid():
            list_obj = form.save()
            messages.success(request, f'Successfully created new catalogue'
                                      f' "{getattr(list_obj, 'catalogue_name')}"')

        else:
            errors = form.errors.as_data()
            for error_field in errors:
                for field_error in errors[error_field]:
                    if field_error.code == 'unique':
                        messages.error(request, f'A catalogue with the {form.fields[error_field].label}'
                                                f' "{form.data[error_field]}" already exists.')
                    elif field_error.code == 'max_length':
                        limit_value = field_error.params['limit_value']
                        show_value = field_error.params['show_value']
                        messages.error(request,
                                       f'{form.fields[error_field].label} can at most have {limit_value}'
                                       f' characters but has {show_value}.')
                    else:
                        messages.error(request, f'Error creating catalogue.')

    return render(request, template,
                  ({
                      'form': form,
                      'catalogue_id': instance and instance.pk,
                  }))

class CatalogueInitView(PermissionRequiredMixin, LoginRequiredMixin, CommonInitFormViewTemplate):
    permission_required = constant.PM_CHANGE_LOOKUPCAT

    def resp_form_page(self, request, form):
        return render(request, 'catalogue/init_form.html', {'form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('catalogue:full_form', new_instance.catalogue_id)

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        return CatalogueForm

class CatalogueSearchView(PermissionRequiredMixin, LoginRequiredMixin, DefaultSearchView):
    permission_required = constant.PM_VIEW_LOOKUPCAT

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('catalogue_name', 'Description',),
            ('publish_status', 'Published',),
        ]

    @property
    def entity(self) -> str:
        return 'Catalogue,Catalogues'

    @property
    def default_order(self) -> str:
        return 'asc'

    @property
    def add_entry_url(self) -> str | None:
        return reverse('catalogue:init_form')

    @property
    def add_entry_url_permission(self) -> str | None:
        return constant.PM_CHANGE_LOOKUPCAT

    @property
    def count_field(self):
        return 'work'

    @property
    def updated_fields(self):
        return ['catalogue_name', 'publish_status', 'owner']

    def get_queryset(self):
        model_class = CofkLookupCatalogue
        request_data = self.request_data.dict()
        if self.request.user.has_perm(constant.PM_CHANGE_LOOKUPCAT):
            return model_class.objects \
                .annotate(**{f'{self.count_field}_count': Count(self.count_field)}).order_by(self.updated_fields[0]).all()
        else:
            return model_class.objects \
                .annotate(**{f'{self.count_field}_count': Count(self.count_field)}).order_by(self.updated_fields[0]).filter(
                owner=self.request.user)


    def get_queryset_by_request_data(self, request_data, sort_by=None):
        queries = query_serv.create_queries_by_field_fn_maps(request_data, self.search_field_fn_maps)

        queryset = query_serv.update_queryset(CofkLookupCatalogue.objects.filter(), CofkLookupCatalogue, queries=queries,
                                              sort_by=self.get_sort_by())

        return queryset

    @property
    def query_fieldset_list(self) -> Iterable:
        return []

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer(
            'catalogue/catalogue_search.html', context_data=self.get_context()
        )

    def get_context(self, **kwargs):
        context = {'can_edit': utils.is_user_editor_or_supervisor(self.request.user)}
        return context
