from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    dependencies = [
        ('audit', '0009_update_trigger_v4'),
    ]

    operations = [
        migrations_utils.update_function_by_file('audit',
                                                 'trigger/dbf_cofk_union_audit_any_v5.sql',
                                                 'trigger/dbf_cofk_union_audit_any_v4.sql'),
    ]
