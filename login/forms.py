from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from login.models import CofkUser


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _("Incorrect username or password. Please note that both fields are case-sensitive."),
    }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CofkUser
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CofkUser
        fields = '__all__'
