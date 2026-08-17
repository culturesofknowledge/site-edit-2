from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_merge_20260721_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mergehistory',
            name='change_user',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='mergehistory',
            name='creation_user',
            field=models.CharField(max_length=254),
        ),
    ]
