from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('audit', '0002_create_audit_trigger'),
        ('core', '0003_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'left_id_value_new', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'left_id_decode_new', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'left_id_value_old', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'left_id_decode_old', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'relationship_decode_left_to_right', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'relationship_decode_right_to_left', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'right_id_value_new', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'right_id_decode_new', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'right_id_value_old', "''"),
        migrations_utils.create_operation_default_value('cofk_union_audit_relationship', 'right_id_decode_old', "''"),
    ]
