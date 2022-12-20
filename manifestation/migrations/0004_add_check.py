from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('manifestation', '0003_sync_old_schema'),
    ]

    operations = [
        migrations_utils.create_operation_zero_one_check('cofk_union_manifestation',
                                                         'manifestation_creation_date_approx',
                                                         'cofk_chk_union_manifestation_creation_date_approx'),
        migrations_utils.create_operation_zero_one_check('cofk_union_manifestation',
                                                         'manifestation_creation_date_inferred',
                                                         'cofk_chk_union_manifestation_creation_date_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_manifestation',
                                                         'manifestation_creation_date_uncertain',
                                                         'cofk_chk_union_manifestation_creation_date_uncertain'),
    ]
