import logging
import operator
import urllib.parse
from functools import reduce
from typing import Iterable

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from cllib import str_utils
from core import constant
from core.helper import renderer_serv, query_serv, view_serv, perm_serv
from core.helper.renderer_serv import RendererFactory
from core.helper.view_serv import DefaultSearchView, DeleteConfirmView
from core.helper.view_serv import FormDescriptor
from core.user_forms import UserSearchFieldset, UserForm
from institution.models import CofkUnionInstitution
from location.models import CofkUnionLocation
from login.models import CofkUser
from login.views import EmloPasswordResetForm
from manifestation.models import CofkUnionManifestation
from person.models import CofkUnionPerson
from publication.models import CofkUnionPublication
from uploader.models import CofkCollectUpload
from work.models import CofkUnionWork

log = logging.getLogger(__name__)


class UserFormDescriptor(FormDescriptor):

    @property
    def name(self):
        return f'{self.obj}'

    @property
    def model_name(self):
        return 'User'


def send_password_reset_email(request, user: CofkUser) -> bool:
    """Email the user a link to set their own password, reusing the same
    token-based flow as the self-service 'forgot password' page (see
    login/urls.py). The supervisor never sees or sets the password."""
    reset_form = EmloPasswordResetForm({'username': user.username})
    if not reset_form.is_valid():
        log.warning(f'could not send password reset email to [{user.username}] -- {reset_form.errors}')
        return False

    if not list(reset_form.get_users(user.username)):
        log.warning(f'password reset email not sent to [{user.username}] '
                    f'-- no matching active user with a usable password and email address')
        return False

    reset_form.save(
        request=request,
        use_https=request.is_secure(),
        from_email=settings.EMAIL_FROM_EMAIL,
        email_template_name='login/password-reset-email.txt',
    )
    log.info(f'password reset email sent to [{user.username}]')
    return True


@login_required
@permission_required(constant.PM_CHANGE_USER)
def full_form(request, pk=None):
    instance: CofkUser = CofkUser.objects.filter(pk=pk).first()
    form = UserForm(request.POST or None, instance=instance)

    reset_email_sent = request.session.pop(pk + '_reset_email_sent', None) if pk else None

    def _render_form():
        return render(request, 'user/init_form.html',
                      ({
                           'form': form,
                           'user_id': instance and instance.pk,
                           'reset_email_sent': reset_email_sent,
                       }
                       | UserFormDescriptor(instance).create_context()
                       | view_serv.create_is_save_success_context(is_save_success)
                       ))

    is_save_success = False
    if request.POST:
        perm_serv.validate_permission_denied(request.user, [constant.PM_CHANGE_USER])

        if view_serv.any_invalid_with_log([
            form,
        ]):
            return _render_form()

        try:
            form.save()
        except ValidationError as e:
            # e.g. CofkUser.save() rejecting a username (email) that's
            # already taken -- report it on the form instead of a 500
            form.add_error('email', e)
            return _render_form()

        is_save_success = view_serv.mark_callback_save_success(request)

        if pk is None:
            # give the new account an initial password nobody (including the
            # supervisor) ever sees, then email the user a link to set their own
            form.instance.set_password(str_utils.create_random_str(32))
            form.instance.save()
            email_sent = send_password_reset_email(request, form.instance)
            request.session[form.instance.pk + '_reset_email_sent'] = email_sent
            return redirect(reverse('user:full_form', kwargs={'pk': form.instance.pk}))

    return _render_form()


class UserSearchView(PermissionRequiredMixin, LoginRequiredMixin,  DefaultSearchView):
    permission_required = constant.PM_CHANGE_USER
    raise_exception = True

    @property
    def sort_by_choices(self) -> list[tuple[str, str]]:
        return [
            ('username', 'Username',),
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

    @property
    def add_entry_url_permission(self) -> str | None:
        return constant.PM_CHANGE_USER

    def get_queryset(self):
        model_class = CofkUser
        request_data = self.request_data.dict()
        if not request_data:
            return model_class.objects.all()

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
        return queryset.prefetch_related('groups')

    @property
    def table_search_results_renderer_factory(self) -> RendererFactory:
        return renderer_serv.create_table_search_results_renderer(
            'user/expanded_search_table_layout.html'
        )

    @property
    def query_fieldset_list(self) -> Iterable:
        return [UserSearchFieldset(self.request_data.dict())]


@login_required
@permission_required(constant.PM_CHANGE_USER)
def reset_password(request, pk):
    user: CofkUser = CofkUser.objects.filter(pk=pk).first()
    if user is None:
        # raise not found 404
        raise Http404()

    if request.POST:
        email_sent = send_password_reset_email(request, user)
        return render(request, 'user/reset_password_completed.html',
                      {'user': user, 'email_sent': email_sent})
    else:
        return render(request, 'user/reset_password.html', {'user': user})




# record types listed on the delete confirmation page, with the label to show them under
USER_RECORD_MODELS = [
    (CofkUnionWork, 'works'),
    (CofkUnionPerson, 'people'),
    (CofkUnionLocation, 'places'),
    (CofkUnionManifestation, 'manifestations'),
    (CofkUnionInstitution, 'repositories'),
    (CofkUnionPublication, 'publications'),
]


def count_user_records(username: str) -> list[tuple[str, int]]:
    """Number of records of each type that were created or last changed by the user.
    Records only store the username as text, so they are unaffected by deleting the user."""
    counts = []
    for model, label in USER_RECORD_MODELS:
        user_fields = [f.name for f in model._meta.get_fields() if f.name in ('creation_user', 'change_user')]
        query = reduce(operator.or_, (Q(**{f: username}) for f in user_fields))
        counts.append((label, model.objects.filter(query).count()))
    counts.append(('uploads', CofkCollectUpload.objects.filter(upload_username=username).count()))
    return counts


class UserDeleteConfirmView(PermissionRequiredMixin, LoginRequiredMixin, DeleteConfirmView):
    permission_required = constant.PM_CHANGE_USER
    raise_exception = True

    def get_model_class(self):
        return CofkUser

    def get_name(self):
        return 'user'

    def get_obj_desc_list(self, obj: CofkUser) -> list[str]:
        if obj is None:
            return ['unknown']

        desc_list = [f'{obj} ({obj.username})']
        counts = [f'{count} {label}' for label, count in count_user_records(obj.username) if count]
        if counts:
            desc_list.append(f'This user created or last changed: {", ".join(counts)}. These records are kept, '
                             f'and will still show {obj.username} in their history.')
        if obj.has_saved_queries:
            desc_list.append('The saved queries of this user will be deleted.')
        return desc_list

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and kwargs.get('obj_id') == request.user.username:
            messages.error(request, 'You cannot delete your own account.')
            return redirect(reverse('user:full_form', args=[request.user.username]))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, obj_id, *args, **kwargs):
        user = self.find_obj_by_obj_id(obj_id)
        if user is None:
            raise Http404()

        # saved queries are removed along with the user (CASCADE); records only
        # reference the username as text, so they are left untouched
        user.delete()
        log.info(f'user [{obj_id}] deleted by [{request.user.username}]')

        msg = urllib.parse.quote(f'User "{obj_id}" deleted successfully')
        return redirect(f'{reverse("user:search")}?to_user_messages={msg}')
