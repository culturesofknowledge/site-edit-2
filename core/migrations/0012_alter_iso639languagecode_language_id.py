# Generated by Django 4.0.6 on 2025-02-26 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_cofklookupcatalogue_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iso639languagecode',
            name='language_id',
            field=models.IntegerField(unique=True),
        ),
    ]
