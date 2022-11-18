# Generated by Django 4.0.6 on 2022-11-17 12:20

import core.helper.model_utils
from django.db import migrations, models
import functools


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0003_cofkworksubjectmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cofkunionwork',
            name='iwork_id',
            field=models.IntegerField(default=functools.partial(core.helper.model_utils.next_seq_safe, *('cofk_union_work_iwork_id_seq',), **{}), unique=True),
        ),
    ]
