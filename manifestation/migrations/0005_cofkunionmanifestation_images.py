# Generated by Django 4.0.6 on 2022-10-21 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0003_alter_iso639languagecode_code_639_3'),
        ('manifestation', '0004_alter_cofkunionlanguageofmanifestation_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='cofkunionmanifestation',
            name='images',
            field=models.ManyToManyField(to='uploader.cofkunionimage'),
        ),
    ]
