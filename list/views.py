import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.views.generic import ListView

from core import constant
from core.forms import CatalogueForm, RoleForm, SubjectForm, OrgTypeForm, ResourceDescriptorForm
from core.helper import perm_serv
from core.models import CofkLookupCatalogue, CofkUnionRoleCategory, CofkUnionSubject, CofkUnionOrgType, \
    CofkUserSavedQuery, CofkResourceDescriptor

from login.utils import get_contributing_editors

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
        return self.model.objects \
            .annotate(**{f'{self.count}_count': Count(self.count)}).order_by(self.updated_fields[0]).all()

    def get_obj_by_id(self):
        if self.model._meta.pk.name in self.request.POST:
            return self.model.objects.filter(pk=self.request.POST[self.model._meta.pk.name]).first()

    def post(self, request, *args, **kwargs):
        perm_serv.validate_permission_denied(self.request.user, self.save_perm)
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
                form = self.form(request.POST, instance=list_obj)
                if form.is_valid():
                    form.save()

                messages.success(request, f'Successfully updated {self.list_type}'
                                          f' "{getattr(list_obj, self.updated_fields[0])}" ({list_obj.pk})')
        elif 'add' in self.request.POST:
            list_form = self.form(self.request.POST)

            # Create new list object
            if list_form.is_valid():
                list_obj = list_form.save()
                messages.success(request, f'Successfully created new {self.list_type}'
                                          f' "{getattr(list_obj, self.updated_fields[0])}"')

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
    def save_perm(self):
        """
        return the permission required to create / save / delete object
        permission format should 'app_name.permission_codename'
        no permission checking if permission is None
        """
        return None

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


class RoleListView(PermissionRequiredMixin, LoginRequiredMixin, CofkListView):
    permission_required = constant.PM_VIEW_ROLECAT
    raise_exception = True
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

    @property
    def save_perm(self):
        return constant.PM_CHANGE_ROLECAT


class CatalogueListView(PermissionRequiredMixin, LoginRequiredMixin, CofkListView):
    permission_required = constant.PM_VIEW_LOOKUPCAT
    raise_exception = True
    model = CofkLookupCatalogue
    template_name = 'catalogue/init_form.html'

    @property
    def form(self):
        return CatalogueForm

    @property
    def count(self):
        return 'work'

    @property
    def updated_fields(self):
        return ['catalogue_name', 'publish_status', 'owner']

    @property
    def list_type(self):
        return 'catalogue'

    @property
    def save_perm(self):
        return constant.PM_CHANGE_LOOKUPCAT

    def get_queryset(self):
        if self.request.user.has_perm(constant.PM_CHANGE_USER):
            return self.model.objects \
                .annotate(**{f'{self.count}_count': Count(self.count)}).order_by(self.updated_fields[0]).all()
        else:
            return self.model.objects \
                .annotate(**{f'{self.count}_count': Count(self.count)}).order_by(self.updated_fields[0]).filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_list'] = get_contributing_editors()

        return context


class SubjectListView(PermissionRequiredMixin, LoginRequiredMixin, CofkListView):
    permission_required = constant.PM_VIEW_SUBJECT
    raise_exception = True
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

    @property
    def save_perm(self):
        return constant.PM_CHANGE_SUBJECT


class OrgTypeListView(PermissionRequiredMixin, LoginRequiredMixin, CofkListView):
    permission_required = constant.PM_VIEW_ORGTYPE
    raise_exception = True
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
        return 'organization type'

    @property
    def save_perm(self):
        return constant.PM_CHANGE_ORGTYPE


class ResourceDescriptorListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    permission_required = constant.PM_VIEW_RESOURCE_DESC
    raise_exception = True
    model = CofkResourceDescriptor
    template_name = 'list/resource_descriptors.html'
    paginate_by = 100

    def get_queryset(self):
        related_to = self.request.GET.get('related_to', '')
        queryset = self.model.objects.all()
        if related_to:
            queryset = queryset.filter(related_to=related_to)
        return queryset.order_by('description')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ResourceDescriptorForm
        context['related_to_choices'] = CofkResourceDescriptor.RELATED_TO_CHOICES
        context['selected_related_to'] = self.request.GET.get('related_to', '')
        context['searched'] = 'related_to' in self.request.GET
        return context

    def post(self, request, *args, **kwargs):
        perm_serv.validate_permission_denied(request.user, constant.PM_CHANGE_RESOURCE_DESC)

        if 'delete' in request.POST:
            pk = request.POST.get('descriptor_id')
            obj = self.model.objects.filter(pk=pk).first()
            if obj:
                msg = f'Successfully deleted resource descriptor "{obj.description}" ({obj.pk})'
                obj.delete()
                messages.success(request, msg)

        elif 'save' in request.POST:
            pk = request.POST.get('descriptor_id')
            obj = self.model.objects.filter(pk=pk).first()
            if obj:
                form = ResourceDescriptorForm(request.POST, instance=obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Successfully updated resource descriptor'
                                              f' "{obj.description}" ({obj.pk})')
                else:
                    for error_field in form.errors.as_data():
                        for field_error in form.errors.as_data()[error_field]:
                            if field_error.code == 'unique_together':
                                messages.error(request, f'A resource descriptor with this description'
                                                        f' and relevant to already exists.')
                            else:
                                messages.error(request, f'Error updating resource descriptor.')

        elif 'add' in request.POST:
            form = ResourceDescriptorForm(request.POST)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f'Successfully created new resource descriptor'
                                          f' "{obj.description}"')
            else:
                errors = form.errors.as_data()
                for error_field in errors:
                    for field_error in errors[error_field]:
                        if field_error.code == 'unique_together':
                            messages.error(request, f'A resource descriptor with this description'
                                                    f' and relevant to already exists.')
                        elif field_error.code == 'max_length':
                            limit_value = field_error.params['limit_value']
                            show_value = field_error.params['show_value']
                            messages.error(request,
                                           f'Description can at most have {limit_value}'
                                           f' characters but has {show_value}.')
                        else:
                            messages.error(request, f'Error creating resource descriptor.')

        return super().get(self, request, *args, **kwargs)


class SavedQueries(ListView):
    model = CofkUserSavedQuery
    template_name = 'list/saved_queries.html'
    paginate_by = 20

    def get_queryset(self):
        return self.model.objects.filter(username=self.request.user.username).all()

    def post(self, request, *args, **kwargs):
        pk_name = self.model._meta.pk.name

        if 'save' in request.POST and pk_name in request.POST:
            # Update
            pk = request.POST[pk_name]
            list_obj = self.model.objects.filter(pk=pk).first()

            if list_obj:
                list_obj.query_title = request.POST['query_title']
                list_obj.save()

                messages.success(request, f'Successfully updated saved query ({pk})')
        elif 'delete' in request.POST and pk_name in request.POST:
            pk = request.POST[pk_name]
            list_obj = self.model.objects.filter(pk=pk).first()

            if list_obj:
                list_obj.delete()

                messages.success(request, f'Successfully deleted saved query ({pk})')
                log.info(f'{request.user.username} deleted saved query {pk}')

        return super().get(self, request, *args, **kwargs)
