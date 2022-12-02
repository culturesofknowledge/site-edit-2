from django.db import migrations

from audit import audit_migrations_utils
from core.helper import migrations_utils

trigger_sql__dbf_cofk_union_audit_any = """
"""


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('audit', '0001_initial'),
        ('location', '0002_initial'),
        ('institution', '0001_initial'),
        ('manifestation', '0001_initial'),
        ('manifestation', '0001_initial'),
        ('publication', '0001_initial'),
    ]
    operations = [

        *migrations_utils.create_default_change_user_timestamp('cofk_union_audit_literal'),
        *migrations_utils.create_default_change_user_timestamp('cofk_union_audit_relationship'),
        # *migrations_utils.create_default_empty('cofk_union_audit_relationship', [
        #     'left_id_value_new',
        #     'left_id_decode_new',
        #     'left_id_value_old',
        #     'left_id_decode_old',
        #     'relationship_decode_left_to_right',
        #     'relationship_decode_right_to_left',
        #     'right_id_value_new',
        #     'right_id_decode_new',
        #     'right_id_value_old',
        #     'right_id_decode_old',
        # ]),

        # create audit trigger functions
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_any.sql'),
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_literal_delete.sql'),
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_literal_insert.sql'),
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_literal_update.sql'),
    ]

    for table_name in [
        'cofk_union_comment',
        'cofk_union_image',
        'cofk_union_institution',
        'cofk_union_location',
        'cofk_union_manifestation',
        'cofk_union_person',
        'cofk_union_publication',
        'cofk_union_relationship',
        'cofk_union_relationship_type',
        'cofk_union_resource',
        # 'cofk_union_role_category',  # have no change_user
        # 'cofk_union_subject',  # have no change_user
        'cofk_union_work',
    ]:
        operations.extend(
            audit_migrations_utils.create_audit_trigger_list(table_name)
        )
