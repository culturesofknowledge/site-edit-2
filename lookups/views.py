import logging

from django.contrib import messages
from django.db.models import Count
from django.views.generic import ListView

from core.forms import CatalogueForm, RoleForm
from core.models import CofkLookupCatalogue, CofkUnionRoleCategory

log = logging.getLogger(__name__)


class RoleListView(ListView):
    model = CofkUnionRoleCategory
    paginate_by = 100
    template_name = 'lookup/professional_categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form to create new catalogue
        context['form'] = RoleForm()
        return context

    def get_queryset(self):
        return CofkUnionRoleCategory.objects.annotate(person_count=Count('person')).order_by('role_category_desc').all()

    def post(self, request, *args, **kwargs):
        log.info(self.request.POST)
        if 'delete' in self.request.POST:
            role = CofkUnionRoleCategory.objects.filter(pk=self.request.POST['role_category_id']).first()

            if role and role.works.count() == 0:
                msg = f'Successfully deleted role {role.role_category_desc}" ({role.role_category_id})'
                role.delete()
                messages.success(request, msg)
        elif 'save' in self.request.POST:
            # Update
            role = CofkUnionRoleCategory.objects.filter(pk=self.request.POST['role_category_id']).first()
            role.role_category_desc = self.request.POST['role_category_desc']
            role.save()

            messages.success(request, f'Successfully updated role "'
                                      f'{role.role_category_desc}" ({role.role_category_id})')
        elif 'add' in self.request.POST:
            cat_form = CatalogueForm(self.request.POST)

            # Create new catalogue
            if cat_form.is_valid():
                saved = cat_form.save()
                messages.success(request, f'Successfully created new role "'
                                          f'{saved.role_category_desc}" ({saved.role_category_id})')

            else:
                errors = cat_form.errors.as_data()
                for error_field in errors:
                    for field_error in errors[error_field]:
                        if field_error.code == 'unique':
                            messages.error(request, f'A catalogue with the {cat_form.fields[error_field].label}'
                                                    f' "{cat_form.data[error_field]}" already exists.')
                        elif field_error.code == 'max_length':
                            limit_value = field_error.params['limit_value']
                            show_value = field_error.params['show_value']
                            messages.error(request,
                                           f'{cat_form.fields[error_field].label} can at most have {limit_value}'
                                           f' characters but has {show_value}.')
                        else:
                            messages.error(request, 'Error creating catalogue.')

        return super().get(self, request, *args, **kwargs)


class CatalogueListView(ListView):
    model = CofkLookupCatalogue
    paginate_by = 100
    template_name = 'lookup/catalogue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form to create new catalogue
        context['form'] = CatalogueForm()
        return context

    def get_queryset(self):
        return CofkLookupCatalogue.objects.annotate(work_count=Count('works')).order_by('catalogue_name').all()

    def post(self, request, *args, **kwargs):
        if 'delete' in self.request.POST:
            cat = CofkLookupCatalogue.objects.filter(pk=self.request.POST['catalogue_id']).first()

            if cat and cat.works.count() == 0:
                msg = f'Successfully deleted catalogue {cat.catalogue_code} {cat.catalogue_name}" ({cat.catalogue_id})'
                cat.delete()
                messages.success(request, msg)
        elif 'save' in self.request.POST:
            # Update
            cat = CofkLookupCatalogue.objects.filter(pk=self.request.POST['catalogue_id']).first()
            cat.catalogue_name = self.request.POST['catalogue_name']
            cat.save()

            messages.success(request, f'Successfully updated catalogue "'
                                      f'{cat.catalogue_code} {cat.catalogue_name}" ({cat.catalogue_id})')
        elif 'add' in self.request.POST:
            cat_form = CatalogueForm(self.request.POST)

            # Create new catalogue
            if cat_form.is_valid():
                saved = cat_form.save()
                messages.success(request, f'Successfully created new catalogue "'
                                          f'{saved.catalogue_code} {saved.catalogue_name}" ({saved.catalogue_id})')

            else:
                errors = cat_form.errors.as_data()
                for error_field in errors:
                    for field_error in errors[error_field]:
                        if field_error.code == 'unique':
                            messages.error(request, f'A catalogue with the {cat_form.fields[error_field].label}'
                                                    f' "{cat_form.data[error_field]}" already exists.')
                        elif field_error.code == 'max_length':
                            limit_value = field_error.params['limit_value']
                            show_value = field_error.params['show_value']
                            messages.error(request,
                                           f'{cat_form.fields[error_field].label} can at most have {limit_value}'
                                           f' characters but has {show_value}.')
                        else:
                            messages.error(request, 'Error creating catalogue.')

        return super().get(self, request, *args, **kwargs)
