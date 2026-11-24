from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.core.exceptions import ValidationError
from django.db import models, transaction

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
    # prompted for (interactively) or required as --forename/--surname/--email
    # by `manage.py createsuperuser`
    REQUIRED_FIELDS = ['forename', 'surname', 'email']

    @property
    def is_supervisor(self):
        # a superuser is meant to have access to every feature
        if self.is_active and self.is_superuser:
            return True
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
        # Usernames are unique regardless of case, so "Bob" blocks "bob" too.
        if self._state.adding and CofkUser.objects.filter(username__iexact=self.username).exists():
            raise ValidationError(f'A user with the username "{self.username}" already exists.')

        super().save(*args, **kwargs)

    @classmethod
    @transaction.atomic
    def rename(cls, old_username: str, new_username: str):
        """Change a username (the primary key) and move every row that
        references it -- roles, permissions, saved queries, catalogues,
        suggestions and admin log entries.

        Text columns such as creation_user/change_user and the audit log are
        not foreign keys and keep the old username, as a record of who did
        what at the time.
        """
        new_username = new_username.strip()
        if new_username == old_username:
            return
        if cls.objects.filter(username__iexact=new_username).exclude(pk=old_username).exists():
            raise ValidationError(f'A user with the username "{new_username}" already exists.')

        # every foreign key to cofk_user is DEFERRABLE INITIALLY DEFERRED, so
        # the references only need to be valid again by the end of the transaction
        cls.objects.filter(pk=old_username).update(username=new_username)
        for rel in cls._meta.get_fields(include_hidden=True):
            if rel.is_relation and rel.auto_created and not rel.concrete and (rel.one_to_many or rel.one_to_one):
                rel.related_model._base_manager.filter(
                    **{rel.field.attname: old_username}
                ).update(**{rel.field.attname: new_username})

    class Meta:
        db_table = 'cofk_user'
