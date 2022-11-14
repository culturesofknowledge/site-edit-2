from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('manifestation', '0001_initial'),
    ]
    operations = [
        migrations_utils.create_operation_seq('cofk_union_manif_manif_id_seq'),
    ]
