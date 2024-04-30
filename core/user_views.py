from typing import Callable, Iterable

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from core import constant
from core.helper import renderer_serv, query_serv, view_serv, perm_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import CommonInitFormViewTemplate, DefaultSearchView
from core.helper.view_serv import FormDescriptor
from core.user_forms import UserSearchFieldset, UserForm
from login.models import CofkUser


class UserFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return f'{self.obj.surname} {self.obj.forename}'

    @property
    def model_name(self):
        return 'User'

class UserInitView(PermissionRequiredMixin, LoginRequiredMixin, CommonInitFormViewTemplate):
    permission_required = constant.PM_CHANGE_USER

    def resp_form_page(self, request, form):
        return render(request, 'core/user_init_form.html', {'form': form})

    def resp_after_saved(self, request, form, new_instance):
        return redirect('user:full_form', new_instance.pk)

    @property
    def form_factory(self) -> Callable[..., ModelForm]:
        return UserForm


@login_required
def full_form(request, pk):
    instance: CofkUser = get_object_or_404(CofkUser, pk=pk)
    form = UserForm(request.POST or None, instance=instance)

    def _render_form():
        return render(request, 'core/user_init_form.html',
                      ({
                           'form': form,
                       }
                       | UserFormDescriptor(instance).create_context()
                       | view_serv.create_is_save_success_context(is_save_success)
                       ))

    is_save_success = False
    if request.POST:
        perm_serv.validate_permission_denied(request.user, constant.PM_CHANGE_USER)

        if view_serv.any_invalid_with_log([
            form,
        ]):
            return _render_form()

        form.save()
        is_save_success = view_serv.mark_callback_save_success(request)

    return _render_form()

class UserSearchView(LoginRequiredMixin, DefaultSearchView):

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('username', 'User name',),
            ('email', 'Email',),
        ]

    @property
    def entity(self) -> str:
        return 'User,Users'

    @property
    def default_order(self) -> str:
        return 'asc'

    @property
    def add_entry_url(self) -> str | None:
        return reverse('user:init_form')

    def get_queryset(self):
        model_class = CofkUser
        request_data = self.request_data.dict()
        if not request_data:
            return model_class.objects.none()


        queries = []
        queries.extend(
            query_serv.create_queries_by_lookup_field(request_data, self.search_fields,
                                                      search_fields_fn_maps={
                                                          'is_staff': query_serv.lookup_fn_true_false,
                                                          'is_active': query_serv.lookup_fn_true_false,
                                                      })
        )
        queryset = model_class.objects.filter()
        queryset = query_serv.update_queryset(queryset, model_class, queries=queries,
                                              sort_by=self.get_sort_by())
        return queryset

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer(
            'core/user_expanded_search_table_layout.html'
        )

    @property
    def query_fieldset_list(self) -> Iterable:
        return [UserSearchFieldset(self.request_data.dict())]
