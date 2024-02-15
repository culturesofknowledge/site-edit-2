from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('person', '0002_create_seq'),
        ('core', '0003_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_birth_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_birth_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_birth_approx', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_death_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_death_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_death_approx', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'gender', "''"),
        migrations_utils.create_operation_default_value('cofk_union_person', 'is_organisation', "''"),
        migrations_utils.create_operation_default_value('cofk_union_person', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_death_calendar', "''"),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_death_is_range', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'flourished_calendar', "''"),
        migrations_utils.create_operation_default_value('cofk_union_person', 'flourished_is_range', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'uuid', 'uuid_generate_v4()'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'flourished_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'flourished_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'flourished_approx', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_birth_calendar', "''"),
        migrations_utils.create_operation_default_value('cofk_union_person', 'date_of_birth_is_range', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person_summary', 'sent', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person_summary', 'recd', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person_summary', 'all_works', '0'),
        migrations_utils.create_operation_default_value('cofk_union_person_summary', 'mentioned', '0'),
    ]
