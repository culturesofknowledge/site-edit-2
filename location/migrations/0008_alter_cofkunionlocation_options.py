# Generated by Django 4.0.6 on 2024-10-02 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0007_alter_cofkunionlocation_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cofkunionlocation',
            options={'permissions': [('export_file', 'Export csv/excel from search results'), ('clonefinder', 'Allow use clonefinder feature to find similar records')]},
        ),
    ]
