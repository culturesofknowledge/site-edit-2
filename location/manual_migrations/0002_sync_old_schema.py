from django.db import migrations

from sharedlib.djangolib import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('location', '0001_initial'),
        ('core', '0003_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_location', 'location_name', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_location', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_1_eg_room', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_2_eg_building', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_3_eg_parish', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_4_eg_city', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_5_eg_county', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_6_eg_country', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'element_7_eg_empire', "''"),
        migrations_utils.create_operation_default_value('cofk_union_location', 'uuid', 'uuid_generate_v4()'),


    ]
