from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('institution', '0001_initial'),
        ('core', '0003_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_institution', 'institution_name', "''"),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'institution_synonyms', "''"),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'institution_city', "''"),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'institution_city_synonyms', "''"),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'institution_country', "''"),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'institution_country_synonyms', "''"),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'creation_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'uuid', 'uuid_generate_v4()'),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'address', 'NULL::character varying'),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'latitude', 'NULL::character varying'),
        migrations_utils.create_operation_default_value('cofk_union_institution', 'longitude', 'NULL::character varying'),


    ]
