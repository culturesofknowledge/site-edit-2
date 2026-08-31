from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.core.exceptions import ValidationError
from django.db import models

from core.models import CofkUserSavedQuery
from core import constant


class CofkUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=254, primary_key=True)

    surname = models.CharField(max_length=30, null=False, default='')
    forename = models.CharField(max_length=30, null=False, default='')
    failed_logins = models.IntegerField(null=False, default=0, blank=True)
    prev_login = models.DateTimeField(null=True, blank=True)
    login_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=False)
    email = models.EmailField(null=True)

    is_staff = models.BooleanField(default=False, help_text='Identifies whether the user can log into the admin site')

    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'

    @property
    def is_supervisor(self):
        return self.groups.filter(name=constant.ROLE_SUPER).exists()

    @property
    def has_saved_queries(self):
        return CofkUserSavedQuery.objects.filter(username=self.username).exists()

    def __str__(self):
        return f"{self.forename} {self.surname}"

    def save(self, *args, **kwargs):
        # username is the PK -- normalise it here so every creation path (the
        # web form, management commands, `createsuperuser`) is protected, not
        # just the ones that happen to run it through a form field first.
        if self.username:
            self.username = self.username.strip()

        # a fresh instance whose (stripped) username already exists would
        # otherwise silently UPDATE that row instead of failing, since save()
        # treats an explicit PK match as an update rather than a conflict.
        if self._state.adding and CofkUser.objects.filter(pk=self.username).exists():
            raise ValidationError(f'A user with the username "{self.username}" already exists.')

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'cofk_user'
