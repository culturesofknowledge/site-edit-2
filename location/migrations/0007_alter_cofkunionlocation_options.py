# Generated by Django 4.0.6 on 2024-09-24 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0006_displayablelocation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cofkunionlocation',
            options={'permissions': [('export_file', 'Export csv/excel from search results'), ('tombstone', 'Allow use tombstone feature to find similar records')]},
        ),
    ]
