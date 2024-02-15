from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('manifestation', '0002_create_seq'),
        ('core', '0003_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'manifestation_type', "''"),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'manifestation_creation_calendar',
                                                        "'U'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_creation_date_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_creation_date_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_creation_date_approx', '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'manifestation_is_translation',
                                                        '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_creation_date_is_range', '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'opened', "'o'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'uuid', 'uuid_generate_v4()'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'manifestation_receipt_calendar',
                                                        "'U'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_receipt_date_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_receipt_date_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation', 'manifestation_receipt_date_approx',
                                                        '0'),
        migrations_utils.create_operation_default_value('cofk_union_manifestation',
                                                        'manifestation_receipt_date_is_range', '0'),
    ]
