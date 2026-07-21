from django import forms
from django.forms import ModelForm

from core import constant
from core.form_label_maps import field_label_map
from core.helper import form_serv, widgets_serv, query_cache_serv
from core.helper.form_serv import BasicSearchFieldset, SearchCharField
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
        if not self.instance.pk:
            del self.fields['username']

    def clean_email(self):
        # the email becomes the username on creation (see save()), which is a
        # CharField(max_length=30) primary key -- reject upfront rather than
        # fail with a raw DB error or a silently truncated username
        email = self.cleaned_data['email']
        username_max_length = CofkUser._meta.get_field('username').max_length
        if not self.instance.pk and len(email) > username_max_length:
            raise forms.ValidationError(
                f'Email is too long to use as a username '
                f'(max {username_max_length} characters, got {len(email)}).'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.pk:
            user.username = self.cleaned_data['email']
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserSearchFieldset(BasicSearchFieldset):
    title = 'User'
    template_name = 'core/component/user_search_fieldset.html'

    username = SearchCharField(
        label=field_label_map['user']['username'],
        help_text='The user name is used to log in to the system.')
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
