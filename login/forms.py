from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from login import utils as login_utils
from login.models import CofkUser


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _("Incorrect username/email or password. Please note that the password is case-sensitive."),
        "multiple_accounts": _("More than one account uses this email address. "
                               "Please log in with your username instead."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Username or email')

    def clean(self):
        username = self.cleaned_data.get('username')
        if username and len(login_utils.find_users_by_login(username)) > 1:
            raise ValidationError(self.error_messages['multiple_accounts'], code='multiple_accounts')
        return super().clean()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CofkUser
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CofkUser
        fields = '__all__'
