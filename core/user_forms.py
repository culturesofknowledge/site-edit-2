from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import transaction
from django.forms import ModelForm

from core import constant
from core.form_label_maps import field_label_map
from core.helper import form_serv, widgets_serv, query_cache_serv
from core.helper.form_serv import BasicSearchFieldset, SearchCharField
from login import utils as login_utils
from login.models import CofkUser


class UserForm(ModelForm):
    username = form_serv.CharField(required=True)
    email = forms.EmailField(required=True, max_length=200)
    forename = forms.CharField(required=True, max_length=200)
    surname = forms.CharField(required=True, max_length=200)
    is_active = form_serv.ZeroOneCheckboxField(is_str=False, required=False, initial=1)
    is_staff = form_serv.ZeroOneCheckboxField(is_str=False, required=False, initial=0)

    class Meta:
        model = CofkUser
        fields = (
            'username',
            'email',
            'forename',
            'surname',
            'is_active',
            'groups',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        group_name_id_map = query_cache_serv.create_group_name_id_map()
        self.fields['groups'].widget = widgets_serv.EmloCheckboxSelectMultiple()
        self.fields['groups'].choices = (
            (group_name_id_map[name], label)
            for name, label in constant.ROLE_DISPLAY_NAMES)
        # the username is generated on creation (see save()) and can only be
        # changed afterwards
        self.original_username = self.instance.pk or None
        if not self.original_username:
            del self.fields['username']

    @property
    def is_renamed(self) -> bool:
        return bool(self.original_username) and self.cleaned_data.get('username') != self.original_username

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if username == self.original_username:
            return username

        username_max_length = CofkUser._meta.get_field('username').max_length
        if len(username) > username_max_length:
            raise forms.ValidationError(f'Username is too long (max {username_max_length} characters).')
        UnicodeUsernameValidator()(username)
        if CofkUser.objects.filter(username__iexact=username).exclude(pk=self.original_username).exists():
            raise forms.ValidationError(f'The username "{username}" is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if not self.original_username:
            user.username = login_utils.generate_username(user.forename, user.surname, user.email)
        if commit:
            with transaction.atomic():
                if self.is_renamed:
                    CofkUser.rename(self.original_username, user.username)
                user.save()
                self.save_m2m()
            query_cache_serv.clear_username_map()
        return user


class UserSearchFieldset(BasicSearchFieldset):
    title = 'User'
    template_name = 'core/component/user_search_fieldset.html'

    username = SearchCharField(
        label=field_label_map['user']['username'],
        help_text='The username is used to log in to the system.')
    username_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)
    surname = SearchCharField(
        label=field_label_map['user']['surname'],
        help_text='The user\'s surname.')
    surname_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)
    forename = SearchCharField(
        label=field_label_map['user']['forename'],
        help_text='The user\'s forename.')
    forename_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)
    is_active = SearchCharField(
        help_text="Is the user active? Inactive users cannot log in to the system.",
        widget=forms.Select(choices=form_serv.none_zero_one_choices))
    email = SearchCharField(
        label=field_label_map['user']['email'],
        help_text='The user\'s email address.')
    email_lookup = form_serv.create_lookup_field(form_serv.StrLookupChoices.choices)
