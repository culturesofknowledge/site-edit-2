# Generated by Django 4.0.6 on 2023-08-16 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0006_alter_cofkcollectaddresseeofwork_iwork_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisplayableCollectWork',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('uploader.cofkcollectwork',),
        ),
        migrations.DeleteModel(
            name='CofkCollectWorkSummary',
        ),
    ]
