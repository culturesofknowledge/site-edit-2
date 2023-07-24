from django.db import migrations

from sharedlib.djangolib import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('audit', '0005_update_trigger'),
    ]
    operations = [
        migrations_utils.update_function_by_file('audit',
                                                 'trigger/dbf_cofk_union_audit_any_v3.sql',
                                                 'trigger/dbf_cofk_union_audit_any_v2.sql'),
    ]
