from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0009_displayablework_alter_cofkunionwork_options'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cofkunionwork',
            index=models.Index(fields=['date_of_work_std'], name='work_date_std_idx'),
        ),
        migrations.AddIndex(
            model_name='cofkunionwork',
            index=models.Index(fields=['date_of_work_std', 'iwork_id'], name='work_date_iwork_idx'),
        ),
        migrations.AddIndex(
            model_name='cofkunionwork',
            index=models.Index(fields=['change_timestamp'], name='work_change_ts_idx'),
        ),
    ]
