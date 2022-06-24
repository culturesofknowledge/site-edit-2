from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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
        'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions',)
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


admin.site.register(CofkUser, CustomUserAdmin)
