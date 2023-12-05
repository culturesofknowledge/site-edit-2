from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('person', '0003_sync_old_schema'),
    ]

    operations = [
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_birth_approx',
                                                         'cofk_chk_union_person_date_of_birth_approx'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_birth_inferred',
                                                         'cofk_chk_union_person_date_of_birth_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_birth_uncertain',
                                                         'cofk_chk_union_person_date_of_birth_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_death_approx',
                                                         'cofk_chk_union_person_date_of_death_approx'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_death_inferred',
                                                         'cofk_chk_union_person_date_of_death_inferred'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_death_uncertain',
                                                         'cofk_chk_union_person_date_of_death_uncertain'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_birth_is_range',
                                                         'cofk_union_chk_date_of_birth_is_range'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'date_of_death_is_range',
                                                         'cofk_union_chk_date_of_death_is_range'),
        migrations_utils.create_operation_zero_one_check('cofk_union_person', 'flourished_is_range',
                                                         'cofk_union_chk_flourished_is_range'),
    ]
