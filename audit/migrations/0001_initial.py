# Generated by Django 4.0.6 on 2022-12-19 14:18

import core.helper.model_utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CofkUnionAuditLiteral',
            fields=[
                ('audit_id', models.AutoField(primary_key=True, serialize=False)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_utils.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('change_type', models.CharField(max_length=3)),
                ('table_name', models.CharField(max_length=100)),
                ('key_value_text', models.CharField(max_length=100)),
                ('key_value_integer', models.IntegerField(blank=True, null=True)),
                ('key_decode', models.TextField(blank=True, null=True)),
                ('column_name', models.CharField(max_length=100)),
                ('new_column_value', models.TextField(blank=True, null=True)),
                ('old_column_value', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cofk_union_audit_literal',
            },
        ),
        migrations.CreateModel(
            name='CofkUnionAuditRelationship',
            fields=[
                ('audit_id', models.AutoField(primary_key=True, serialize=False)),
                ('change_timestamp', models.DateTimeField(blank=True, default=core.helper.model_utils.default_current_timestamp, null=True)),
                ('change_user', models.CharField(max_length=50)),
                ('change_type', models.CharField(max_length=3)),
                ('left_table_name', models.CharField(max_length=100)),
                ('left_id_value_new', models.CharField(max_length=100)),
                ('left_id_decode_new', models.TextField()),
                ('left_id_value_old', models.CharField(max_length=100)),
                ('left_id_decode_old', models.TextField()),
                ('relationship_type', models.CharField(max_length=100)),
                ('relationship_decode_left_to_right', models.CharField(max_length=100)),
                ('relationship_decode_right_to_left', models.CharField(max_length=100)),
                ('right_table_name', models.CharField(max_length=100)),
                ('right_id_value_new', models.CharField(max_length=100)),
                ('right_id_decode_new', models.TextField()),
                ('right_id_value_old', models.CharField(max_length=100)),
                ('right_id_decode_old', models.TextField()),
            ],
            options={
                'db_table': 'cofk_union_audit_relationship',
            },
        ),
    ]
