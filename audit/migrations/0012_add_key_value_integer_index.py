from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0011_update_trigger_v6'),
    ]
    operations = [
        migrations_utils.create_operation_add_index(
            'cofk_union_audit_literal_table_name_key_value_integer', 'cofk_union_audit_literal',
            ['table_name', 'key_value_integer']),
    ]
