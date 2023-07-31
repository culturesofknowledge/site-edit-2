from django.db import migrations

from sharedlib.djangolib import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('work', '0001_initial'),
    ]
    operations = [
        migrations_utils.create_operation_seq('cofk_union_work_iwork_id_seq'),
    ]
