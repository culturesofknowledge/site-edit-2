import logging

from django.contrib import messages
from django.db.models import Count
from django.views.generic import ListView

from core.forms import CatalogueForm, RoleForm, SubjectForm, OrgTypeForm
from core.models import CofkLookupCatalogue, CofkUnionRoleCategory, CofkUnionSubject, CofkUnionOrgType

log = logging.getLogger(__name__)


class CofkListView(ListView):
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form to create new list object
        context['form'] = self.form
        return context

    def get_queryset(self):
        # When a group by is used, as with annotate, the default ordering is ignored.
        # see https://docs.djangoproject.com/en/dev/releases/2.2/#features-deprecated-in-2-2
        # The ordering will be done by the first of the fields to be updated.
        return self.model.objects\
            .annotate(**{f'{self.count}_count': Count(self.count)}).order_by(self.updated_fields[0]).all()

    def get_obj_by_id(self):
        if self.model._meta.pk.name in self.request.POST:
            return self.model.objects.filter(pk=self.request.POST[self.model._meta.pk.name]).first()

    def post(self, request, *args, **kwargs):
        log.info(self.request.POST)
        if 'delete' in self.request.POST:
            list_obj = self.get_obj_by_id()

            if list_obj and getattr(list_obj, self.count).count() == 0:
                msg = f'Successfully deleted {self.list_type}' \
                      f' "{getattr(list_obj, self.updated_fields[0])}" ({list_obj.pk})'
                list_obj.delete()
                messages.success(request, msg)
        elif 'save' in self.request.POST:
            # Update
            list_obj = self.get_obj_by_id()

            if list_obj:
                for attr in self.updated_fields:
                    setattr(list_obj, attr, self.request.POST[attr] if attr in self.request.POST else 0)
                list_obj.save()

                messages.success(request, f'Successfully updated {self.list_type}'
                                          f' "{getattr(list_obj, self.updated_fields[0])}"({list_obj.pk})')
        elif 'add' in self.request.POST:
            list_form = self.form(self.request.POST)

            # Create new list object
            if list_form.is_valid():
                list_obj = list_form.save()
                messages.success(request, f'Successfully created new {self.list_type}'
                                          f' "{getattr(list_obj, self.updated_fields[0])}"({list_obj.pk})')

            else:
                errors = list_form.errors.as_data()
                for error_field in errors:
                    for field_error in errors[error_field]:
                        if field_error.code == 'unique':
                            messages.error(request, f'A {self.list_type} with the {list_form.fields[error_field].label}'
                                                    f' "{list_form.data[error_field]}" already exists.')
                        elif field_error.code == 'max_length':
                            limit_value = field_error.params['limit_value']
                            show_value = field_error.params['show_value']
                            messages.error(request,
                                           f'{list_form.fields[error_field].label} can at most have {limit_value}'
                                           f' characters but has {show_value}.')
                        else:
                            messages.error(request, f'Error creating {self.list_type}.')

        return super().get(self, request, *args, **kwargs)

    @property
    def form(self):
        raise NotImplementedError

    @property
    def count(self):
        raise NotImplementedError

    @property
    def list_type(self):
        raise NotImplementedError

    @property
    def updated_fields(self):
        raise NotImplementedError


class RoleListView(CofkListView):
    model = CofkUnionRoleCategory
    template_name = 'list/roles.html'

    @property
    def form(self):
        return RoleForm

    @property
    def count(self):
        return 'person'

    @property
    def updated_fields(self):
        return ['role_category_desc']

    @property
    def list_type(self):
        return 'role'


class CatalogueListView(CofkListView):
    model = CofkLookupCatalogue
    template_name = 'list/catalogue.html'

    @property
    def form(self):
        return CatalogueForm

    @property
    def count(self):
        return 'work'

    @property
    def updated_fields(self):
        return ['catalogue_name', 'publish_status']

    @property
    def list_type(self):
        return 'catalogue'


class SubjectListView(CofkListView):
    model = CofkUnionSubject
    template_name = 'list/subjects.html'

    @property
    def form(self):
        return SubjectForm

    @property
    def count(self):
        return 'work'

    @property
    def updated_fields(self):
        return ['subject_desc']

    @property
    def list_type(self):
        return 'subject'


class OrgTypeListView(CofkListView):
    model = CofkUnionOrgType
    template_name = 'list/orgtypes.html'

    @property
    def form(self):
        return OrgTypeForm

    @property
    def count(self):
        return 'person'

    @property
    def updated_fields(self):
        return ['org_type_desc']

    @property
    def list_type(self):
        return 'organisation type'
