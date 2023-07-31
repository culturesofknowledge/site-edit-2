from django.db import migrations

from sharedlib.djangolib import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0003_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_relationship_type', 'desc_left_to_right', "''"),
        migrations_utils.create_operation_default_value('cofk_union_relationship_type', 'desc_right_to_left', "''"),
        migrations_utils.create_operation_default_value('cofk_union_relationship_type', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_relationship_type', 'change_timestamp', 'now()'),

        migrations_utils.create_operation_default_value('cofk_union_comment', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_comment', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_comment', 'uuid', 'uuid_generate_v4()'),
        migrations_utils.create_operation_default_value('cofk_union_nationality', 'nationality_desc', "''"),
        migrations_utils.create_operation_default_value('cofk_union_resource', 'resource_name', "''"),
        migrations_utils.create_operation_default_value('cofk_union_resource', 'resource_details', "''"),
        migrations_utils.create_operation_default_value('cofk_union_resource', 'resource_url', "''"),
        migrations_utils.create_operation_default_value('cofk_union_resource', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_resource', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_resource', 'uuid', 'uuid_generate_v4()'),
        migrations_utils.create_operation_default_value('cofk_union_speed_entry_text', 'object_type', "'All'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_speed_entry_text', 'speed_entry_text', "''"),

        migrations_utils.create_operation_default_value('cofk_union_image', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_image', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_image', 'can_be_displayed', "'Y'::character varying"),
        migrations_utils.create_operation_default_value('cofk_union_image', 'display_order', '1'),
        migrations_utils.create_operation_default_value('cofk_union_image', 'licence_details', "''"),
        migrations_utils.create_operation_default_value('cofk_union_image', 'licence_url', "''"),
        migrations_utils.create_operation_default_value('cofk_union_image', 'credits', "''"),
        migrations_utils.create_operation_default_value('cofk_union_image', 'uuid', 'uuid_generate_v4()'),

        migrations_utils.create_operation_default_value('cofk_union_org_type', 'org_type_desc', "''"),
        migrations_utils.create_operation_default_value('cofk_union_role_category', 'role_category_desc', "''"),
        migrations_utils.create_operation_default_value('cofk_union_subject', 'subject_desc', "''"),
        migrations_utils.create_operation_default_value('iso_639_language_codes', 'code_639_3', "''"),
        migrations_utils.create_operation_default_value('iso_639_language_codes', 'code_639_1', "''"),
        migrations_utils.create_operation_default_value('iso_639_language_codes', 'language_name', "''"),
        migrations_utils.create_operation_default_value('cofk_user_saved_query_selection', 'column_value2', "''"),

        migrations_utils.create_operation_default_value('cofk_lookup_catalogue', 'catalogue_code', "''"),
        migrations_utils.create_operation_default_value('cofk_lookup_catalogue', 'catalogue_name', "''"),
        migrations_utils.create_operation_default_value('cofk_lookup_catalogue', 'is_in_union', '1'),
        migrations_utils.create_operation_default_value('cofk_lookup_catalogue', 'publish_status', '0'),

    ]
