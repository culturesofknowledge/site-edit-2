# Generated by Django 4.0.5 on 2022-06-17 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cofkcollectlocationresource',
            name='upload_id',
        ),
        migrations.DeleteModel(
            name='CofkCollectLocation',
        ),
        migrations.DeleteModel(
            name='CofkCollectLocationResource',
        ),
        migrations.DeleteModel(
            name='CofkUnionLocation',
        ),
    ]