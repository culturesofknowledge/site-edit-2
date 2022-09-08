# Generated by Django 4.0.6 on 2022-09-08 13:43

import core.helper.model_utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_alter_cofkunionlocation_change_timestamp_and_more'),
        ('person', '0009_alter_cofkpersonlocationmap_person'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cofkpersonlocationmap',
            old_name='person_location_id',
            new_name='recref_id',
        ),
        migrations.CreateModel(
            name='CofkPersonOrganisationMap',
            fields=[
                ('recref_id', models.AutoField(primary_key=True, serialize=False)),
                ('from_date', models.DateField(null=True)),
                ('to_date', models.DateField(null=True)),
                ('relationship_type', models.CharField(max_length=100)),
                ('creation_timestamp', models.DateTimeField(blank=True, default=core.helper.model_utils.default_current_timestamp, null=True)),
                ('creation_user', models.CharField(max_length=50)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_utils.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.cofkunionlocation')),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organisation', to='person.cofkunionperson', to_field='iperson_id')),
                ('owner_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner_person', to='person.cofkunionperson', to_field='iperson_id')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.cofkunionperson', to_field='iperson_id')),
            ],
            options={
                'db_table': 'cofk_person_person_map',
                'abstract': False,
            },
            bases=(models.Model, core.helper.model_utils.RecordTracker),
        ),
    ]
