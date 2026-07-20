from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    dependencies = [
        ('audit', '0007_update_audit_literal_helpers'),
    ]
    operations = [
        migrations_utils.update_function_by_file('audit',
                                                 'trigger/dbf_cofk_union_audit_any_v4.sql',
                                                 'trigger/dbf_cofk_union_audit_any_v3.sql'),
    ]
