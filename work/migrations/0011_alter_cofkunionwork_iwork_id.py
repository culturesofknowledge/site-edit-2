# Generated by Django 4.0.6 on 2025-02-26 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0010_alter_cofkunionlanguageofwork_language_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cofkunionwork',
            name='iwork_id',
            field=models.IntegerField(unique=True),
        ),
    ]
