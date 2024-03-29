# Generated by Django 4.0.6 on 2022-12-22 14:26

import functools

import django.db.models.deletion
from django.db import migrations, models

import core.helper.model_serv


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('location', '0001_initial'),
        ('core', '0001_initial'),
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CofkUnionWork',
            fields=[
                ('work_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_of_work_as_marked', models.CharField(blank=True, max_length=250, null=True)),
                ('original_calendar', models.CharField(default='', max_length=2)),
                ('date_of_work_std', models.CharField(blank=True, default='9999-12-31', max_length=12, null=True)),
                ('date_of_work_std_gregorian', models.CharField(blank=True, default='9999-12-31', max_length=12, null=True)),
                ('date_of_work_std_year', models.IntegerField(blank=True, null=True)),
                ('date_of_work_std_month', models.IntegerField(blank=True, null=True)),
                ('date_of_work_std_day', models.IntegerField(blank=True, null=True)),
                ('date_of_work2_std_year', models.IntegerField(blank=True, null=True)),
                ('date_of_work2_std_month', models.IntegerField(blank=True, null=True)),
                ('date_of_work2_std_day', models.IntegerField(blank=True, null=True)),
                ('date_of_work_std_is_range', models.SmallIntegerField(default=0)),
                ('date_of_work_inferred', models.SmallIntegerField(default=0)),
                ('date_of_work_uncertain', models.SmallIntegerField(default=0)),
                ('date_of_work_approx', models.SmallIntegerField(default=0)),
                ('authors_as_marked', models.TextField(blank=True, null=True)),
                ('addressees_as_marked', models.TextField(blank=True, null=True)),
                ('authors_inferred', models.SmallIntegerField(default=0)),
                ('authors_uncertain', models.SmallIntegerField(default=0)),
                ('addressees_inferred', models.SmallIntegerField(default=0)),
                ('addressees_uncertain', models.SmallIntegerField(default=0)),
                ('destination_as_marked', models.TextField(blank=True, null=True)),
                ('origin_as_marked', models.TextField(blank=True, null=True)),
                ('destination_inferred', models.SmallIntegerField(default=0)),
                ('destination_uncertain', models.SmallIntegerField(default=0)),
                ('origin_inferred', models.SmallIntegerField(default=0)),
                ('origin_uncertain', models.SmallIntegerField(default=0)),
                ('abstract', models.TextField(blank=True, null=True)),
                ('keywords', models.TextField(blank=True, null=True)),
                ('language_of_work', models.CharField(blank=True, max_length=255, null=True)),
                ('work_is_translation', models.SmallIntegerField(default=0)),
                ('incipit', models.TextField(blank=True, null=True)),
                ('explicit', models.TextField(blank=True, null=True)),
                ('ps', models.TextField(blank=True, null=True)),
                ('accession_code', models.CharField(blank=True, max_length=1000, null=True)),
                ('work_to_be_deleted', models.SmallIntegerField(default=0)),
                ('iwork_id', models.IntegerField(default=functools.partial(core.helper.model_serv.next_seq_safe, *('cofk_union_work_iwork_id_seq',), **{}), unique=True)),
                ('editors_notes', models.TextField(blank=True, null=True)),
                ('edit_status', models.CharField(default='', max_length=3)),
                ('relevant_to_cofk', models.CharField(default='Y', max_length=3)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('uuid', models.UUIDField(blank=True, default=core.helper.model_serv.default_uuid, null=True)),
                ('original_catalogue', models.ForeignKey(blank=True, db_column='original_catalogue', db_constraint=False, default='', on_delete=django.db.models.deletion.DO_NOTHING, to='core.cofklookupcatalogue', to_field='catalogue_code')),
            ],
            options={
                'db_table': 'cofk_union_work',
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkWorkWorkMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('work_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_from_set', to='work.cofkunionwork')),
                ('work_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_to_set', to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_work_work_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkWorkSubjectMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cofkunionsubject')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_work_subject_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkWorkResourceMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cofkunionresource')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_work_resource_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkWorkPersonMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.cofkunionperson')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_work_person_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkWorkLocationMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.cofkunionlocation')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_work_location_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkWorkCommentMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cofkunioncomment')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_work_comment_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_serv.RecordTracker),
        ),
        migrations.CreateModel(
            name='CofkUnionQueryableWork',
            fields=[
                ('iwork_id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_of_work_std', models.DateField(blank=True, null=True)),
                ('date_of_work_std_year', models.IntegerField(blank=True, null=True)),
                ('date_of_work_std_month', models.IntegerField(blank=True, null=True)),
                ('date_of_work_std_day', models.IntegerField(blank=True, null=True)),
                ('date_of_work_as_marked', models.CharField(blank=True, max_length=250, null=True)),
                ('date_of_work_inferred', models.SmallIntegerField()),
                ('date_of_work_uncertain', models.SmallIntegerField()),
                ('date_of_work_approx', models.SmallIntegerField()),
                ('creators_searchable', models.TextField()),
                ('creators_for_display', models.TextField()),
                ('authors_as_marked', models.TextField(blank=True, null=True)),
                ('notes_on_authors', models.TextField(blank=True, null=True)),
                ('authors_inferred', models.SmallIntegerField()),
                ('authors_uncertain', models.SmallIntegerField()),
                ('addressees_searchable', models.TextField()),
                ('addressees_for_display', models.TextField()),
                ('addressees_as_marked', models.TextField(blank=True, null=True)),
                ('addressees_inferred', models.SmallIntegerField()),
                ('addressees_uncertain', models.SmallIntegerField()),
                ('places_from_searchable', models.TextField()),
                ('places_from_for_display', models.TextField()),
                ('origin_as_marked', models.TextField(blank=True, null=True)),
                ('origin_inferred', models.SmallIntegerField()),
                ('origin_uncertain', models.SmallIntegerField()),
                ('places_to_searchable', models.TextField()),
                ('places_to_for_display', models.TextField()),
                ('destination_as_marked', models.TextField(blank=True, null=True)),
                ('destination_inferred', models.SmallIntegerField()),
                ('destination_uncertain', models.SmallIntegerField()),
                ('manifestations_searchable', models.TextField()),
                ('manifestations_for_display', models.TextField()),
                ('abstract', models.TextField(blank=True, null=True)),
                ('keywords', models.TextField(blank=True, null=True)),
                ('people_mentioned', models.TextField(blank=True, null=True)),
                ('images', models.TextField(blank=True, null=True)),
                ('related_resources', models.TextField(blank=True, null=True)),
                ('language_of_work', models.CharField(blank=True, max_length=255, null=True)),
                ('work_is_translation', models.SmallIntegerField()),
                ('flags', models.TextField(blank=True, null=True)),
                ('edit_status', models.CharField(max_length=3)),
                ('general_notes', models.TextField(blank=True, null=True)),
                ('original_catalogue', models.CharField(max_length=100)),
                ('accession_code', models.CharField(blank=True, max_length=1000, null=True)),
                ('work_to_be_deleted', models.SmallIntegerField()),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_serv.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('drawer', models.CharField(blank=True, max_length=50, null=True)),
                ('editors_notes', models.TextField(blank=True, null=True)),
                ('manifestation_type', models.CharField(blank=True, max_length=50, null=True)),
                ('original_notes', models.TextField(blank=True, null=True)),
                ('relevant_to_cofk', models.CharField(max_length=1)),
                ('subjects', models.TextField(blank=True, null=True)),
                ('work', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_union_queryable_work',
            },
        ),
        migrations.CreateModel(
            name='CofkUnionLanguageOfWork',
            fields=[
                ('lang_work_id', models.AutoField(primary_key=True, serialize=False)),
                ('notes', models.CharField(blank=True, max_length=100, null=True)),
                ('language_code', models.ForeignKey(db_column='language_code', on_delete=django.db.models.deletion.DO_NOTHING, to='core.iso639languagecode')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='language_set', to='work.cofkunionwork')),
            ],
            options={
                'db_table': 'cofk_union_language_of_work',
                'unique_together': {('work', 'language_code')},
            },
        ),
    ]
