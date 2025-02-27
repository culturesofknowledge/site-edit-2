# Generated by Django 4.0.6 on 2025-02-27 10:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CofkSuggestions',
            fields=[
                ('suggestion_id', models.AutoField(primary_key=True, serialize=False)),
                ('suggestion_new', models.BooleanField(default=True)),
                ('suggestion_type', models.CharField(max_length=200)),
                ('suggestion_suggestion', models.TextField()),
                ('suggestion_status', models.CharField(default='New', max_length=256)),
                ('suggestion_created_at', models.DateTimeField(auto_now_add=True)),
                ('suggestion_updated_at', models.DateTimeField(auto_now=True)),
                ('suggestion_resolved_at', models.DateTimeField(blank=True, null=True)),
                ('suggestion_related_record_int', models.IntegerField(blank=True, null=True)),
                ('suggestion_author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suggestions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cofk_union_suggestions',
            },
        ),
    ]
