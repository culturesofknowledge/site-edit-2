from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import _unicode_ci_compare
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.template import loader
from django.utils.http import urlsafe_base64_encode

from core.helper import exporter_serv

UserModel = get_user_model()

@login_required
def dashboard(request):
    return render(request, 'login/dashboard.html', {
        'is_exporting': exporter_serv.is_exporter_pending(),
    })

@login_required
def password_changed(request):
    return render(request, 'login/password-changed.html')


def _consume_pending_messages(request):
    for _msg in messages.get_messages(request):
        pass


class EmloLoginView(LoginView):
    template_name = 'login/login.html'

    def form_valid(self, form):
        _consume_pending_messages(self.request)
        return super().form_valid(form)


class EmloLogoutView(LogoutView):
    next_page = 'login:gate'

    def dispatch(self, request, *args, **kwargs):
        _consume_pending_messages(request)
        return super().dispatch(request, *args, **kwargs)


class EmloPasswordResetForm(forms.Form):
    username = forms.fields.CharField(
        label=_("User name"),
        max_length=254,
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()

    def get_users(self, username):
        """Given an username, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % UserModel.USERNAME_FIELD: username,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(username, getattr(u, UserModel.USERNAME_FIELD))
        )

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        username = self.cleaned_data["username"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(username):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )

class EmloPasswordResetView(PasswordResetView):
    form_class = EmloPasswordResetForm