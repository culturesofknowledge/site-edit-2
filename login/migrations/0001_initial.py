# Generated by Django 4.0.6 on 2022-07-11 12:34

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CofkUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('surname', models.CharField(default='', max_length=30)),
                ('forename', models.CharField(default='', max_length=30)),
                ('failed_logins', models.IntegerField(blank=True, default=0)),
                ('prev_login', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CofkRoles',
            fields=[
                ('role_id', models.AutoField(primary_key=True, serialize=False)),
                ('role_code', models.CharField(max_length=20, unique=True)),
                ('role_name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CofkSessions',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False)),
                ('session_timestamp', models.DateTimeField()),
                ('session_code', models.TextField(blank=True, null=True, unique=True)),
                ('username', models.ForeignKey(blank=True, db_column='username', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CofkUserRoles',
            fields=[
                ('username', models.OneToOneField(db_column='username', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='login.cofkroles')),
            ],
            options={
                'db_table': 'cofk_user_roles',
                'unique_together': {('username', 'role')},
            },
        ),
    ]
