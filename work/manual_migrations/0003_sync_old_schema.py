from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('work', '0002_create_seq'),
        ('core', '0002_basic_db_settings'),
    ]
    operations = [

        migrations_utils.create_operation_default_value('cofk_union_work', 'original_calendar', "''"),
        migrations_utils.create_operation_default_value('cofk_union_work', 'date_of_work_std',
                                                        "'9999-12-31'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_work', 'date_of_work_std_gregorian',
                                                        "'9999-12-31'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_work', 'date_of_work_std_is_range', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'date_of_work_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'date_of_work_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'date_of_work_approx', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'authors_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'authors_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'addressees_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'addressees_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'destination_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'destination_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'origin_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'origin_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'work_is_translation', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'work_to_be_deleted', '0'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'edit_status', "''"),
        migrations_utils.create_operation_default_value('cofk_union_work', 'relevant_to_cofk',
                                                        "'Y'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_work', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'uuid', 'uuid_generate_v4()'),
        migrations_utils.create_operation_default_value('cofk_union_work', 'original_catalogue', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'date_of_work_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'date_of_work_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'date_of_work_approx', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'creators_searchable', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'creators_for_display', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'authors_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'authors_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'addressees_searchable', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'addressees_for_display', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'addressees_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'addressees_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'places_from_searchable', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'places_from_for_display', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'origin_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'origin_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'places_to_searchable', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'places_to_for_display', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'destination_inferred', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'destination_uncertain', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'manifestations_searchable', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'manifestations_for_display',
                                                        "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'work_is_translation', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'edit_status', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'original_catalogue', "''"),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'work_to_be_deleted', '0'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_queryable_work', 'relevant_to_cofk', "''"),

    ]
