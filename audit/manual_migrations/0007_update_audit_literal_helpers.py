from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    dependencies = [
        ('audit', '0006_update_trigger_drop_queryable'),
    ]

    operations = [
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_literal_insert.sql'),
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_literal_update.sql'),
        migrations_utils.create_function_by_file('audit', 'trigger/dbf_cofk_union_audit_literal_delete.sql'),
    ]
