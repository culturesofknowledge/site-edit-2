# Generated by Django 4.0.6 on 2023-04-05 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_cofkusersavedquery_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cofkusersavedquery',
            options={'ordering': ['-creation_timestamp']},
        ),
        migrations.AlterField(
            model_name='cofkusersavedqueryselection',
            name='query',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selection', to='core.cofkusersavedquery'),
        ),
    ]
