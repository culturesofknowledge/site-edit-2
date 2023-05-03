from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AuthenticationForm

from core import constant
# Register your models here.
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CofkUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CofkUser
    list_display = ['username', 'surname', 'email', 'is_active', 'failed_logins', 'last_login']
    search_fields = ['username', 'surname', 'forename', 'email', ]

    _personal_fieldsets = ("Personal info", {"fields": ('surname', 'forename', 'email',)})
    _permission_fieldsets = ("Permission", {
        'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions',)
    })
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        _personal_fieldsets,
        _permission_fieldsets,
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2",
                           ),
            },
        ),
        _personal_fieldsets,
        _permission_fieldsets,
    )

    def has_view_or_change_permission(self, request, obj=None):
        return request.user.has_perm(constant.PM_CHANGE_USER)

    def has_module_permission(self, request):
        return request.user.has_perm(constant.PM_CHANGE_USER)


admin.site.register(CofkUser, CustomUserAdmin)
