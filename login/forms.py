from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from login.models import CofkUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CofkUser
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CofkUser
        fields = '__all__'
