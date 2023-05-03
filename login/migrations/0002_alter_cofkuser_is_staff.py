# Generated by Django 4.0.6 on 2023-05-01 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cofkuser',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Identifies whether the user can log into the admin site'),
        ),
    ]