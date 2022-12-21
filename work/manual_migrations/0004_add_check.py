from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('work', '0003_sync_old_schema'),
    ]

    operations = [
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'addressees_inferred',
                                                         'cofk_chk_union_work_addressees_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'addressees_uncertain',
                                                         'cofk_chk_union_work_addressees_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'authors_inferred',
                                                         'cofk_chk_union_work_authors_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'authors_uncertain',
                                                         'cofk_chk_union_work_authors_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'date_of_work_approx',
                                                         'cofk_chk_union_work_date_of_work_approx'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'date_of_work_inferred',
                                                         'cofk_chk_union_work_date_of_work_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'date_of_work_std_is_range',
                                                         'cofk_chk_union_work_date_of_work_std_is_range'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'date_of_work_uncertain',
                                                         'cofk_chk_union_work_date_of_work_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'destination_inferred',
                                                         'cofk_chk_union_work_destination_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'destination_uncertain',
                                                         'cofk_chk_union_work_destination_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'work_is_translation',
                                                         'cofk_chk_union_work_is_translation'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'origin_inferred',
                                                         'cofk_chk_union_work_origin_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'origin_uncertain',
                                                         'cofk_chk_union_work_origin_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_work', 'work_to_be_deleted',
                                                         'cofk_chk_union_work_to_be_deleted'),
    ]
