from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models

# KTODO copy role and group models

# Create your models here.

class CofkUser(AbstractBaseUser, PermissionsMixin):
    # class Meta:
    #     db_table = 'cofk_users'

    username = models.CharField(max_length=30, primary_key=True)
    # pw changed from Textfield
    # pw = models.CharField(max_length=100, null=False)
    surname = models.CharField(max_length=30, null=False, default='')
    forename = models.CharField(max_length=30, null=False, default='')
    failed_logins = models.IntegerField(null=False, default=0)
    # KTODO should we remove this field? seem duplciated with AbstractBaseUser.last_login
    login_time = models.DateTimeField(null=True)
    prev_login = models.DateTimeField(null=True)
    # Active changed to boolean
    # active = models.SmallIntegerField(null=False, default=1)
    active = models.BooleanField(default=True, null=False)
    # Can be changed to email field
    # email = models.TextField()
    email = models.EmailField(null=True)

    is_staff = models.BooleanField(default=False)  # KTODO required by django, can be remove?



    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
