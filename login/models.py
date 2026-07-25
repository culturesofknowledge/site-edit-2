from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
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

    class Meta:
        db_table = 'cofk_user'
