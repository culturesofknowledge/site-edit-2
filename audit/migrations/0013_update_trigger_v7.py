from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    dependencies = [
        ('audit', '0012_add_key_value_integer_index'),
    ]

    operations = [
        migrations_utils.update_function_by_file('audit',
                                                 'trigger/dbf_cofk_union_audit_any_v7.sql',
                                                 'trigger/dbf_cofk_union_audit_any_v6.sql'),
    ]
