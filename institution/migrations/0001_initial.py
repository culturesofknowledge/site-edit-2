# Generated by Django 4.0.6 on 2022-09-30 11:28

import core.helper.model_utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CofkCollectInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_id', models.IntegerField()),
                ('institution_name', models.TextField()),
                ('institution_city', models.TextField()),
                ('institution_country', models.TextField()),
                ('upload_name', models.CharField(blank=True, max_length=254, null=True)),
                ('_id', models.CharField(blank=True, max_length=32, null=True)),
                ('institution_synonyms', models.TextField(blank=True, null=True)),
                ('institution_city_synonyms', models.TextField(blank=True, null=True)),
                ('institution_country_synonyms', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cofk_collect_institution',
            },
        ),
        migrations.CreateModel(
            name='CofkCollectInstitutionResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_id', models.IntegerField()),
                ('institution_id', models.IntegerField()),
                ('resource_name', models.TextField()),
                ('resource_details', models.TextField()),
                ('resource_url', models.TextField()),
            ],
            options={
                'db_table': 'cofk_collect_institution_resource',
            },
        ),
        migrations.CreateModel(
            name='CofkUnionInstitution',
            fields=[
                ('institution_id', models.AutoField(primary_key=True, serialize=False)),
                ('institution_name', models.TextField()),
                ('institution_synonyms', models.TextField()),
                ('institution_city', models.TextField()),
                ('institution_city_synonyms', models.TextField()),
                ('institution_country', models.TextField()),
                ('institution_country_synonyms', models.TextField()),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_utils.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_utils.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('editors_notes', models.TextField(blank=True, null=True)),
                ('uuid', models.UUIDField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=1000, null=True)),
                ('latitude', models.CharField(blank=True, max_length=20, null=True)),
                ('longitude', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'cofk_union_institution',
            },
            bases=(models.Model, core.helper.model_utils.RecordTracker),
        ),
    ]
