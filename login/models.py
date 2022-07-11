from django.db import models


# KTODO copy role and group models

# Create your models here.

class CofkUsers(models.Model):
    username = models.CharField(primary_key=True, max_length=30)
    pw = models.TextField()
    surname = models.CharField(max_length=30)
    forename = models.CharField(max_length=30)
    failed_logins = models.IntegerField()
    login_time = models.DateTimeField(blank=True, null=True)
    prev_login = models.DateTimeField(blank=True, null=True)
    active = models.SmallIntegerField()
    email = models.TextField(blank=True, null=True)


class CofkRoles(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_code = models.CharField(unique=True, max_length=20)
    role_name = models.TextField(unique=True)


class CofkSessions(models.Model):
    session_id = models.AutoField(primary_key=True)
    session_timestamp = models.DateTimeField()
    session_code = models.TextField(unique=True, blank=True, null=True)
    username = models.ForeignKey('CofkUsers', models.DO_NOTHING, db_column='username', blank=True, null=True)


class CofkUserRoles(models.Model):
    username = models.OneToOneField('CofkUsers', models.DO_NOTHING, db_column='username', primary_key=True)
    role = models.ForeignKey(CofkRoles, models.DO_NOTHING)

    class Meta:
        db_table = 'cofk_user_roles'
        unique_together = (('username', 'role'),)
