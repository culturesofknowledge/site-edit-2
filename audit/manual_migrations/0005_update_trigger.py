from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('audit', '0004_add_index'),
    ]
    operations = [
        migrations_utils.update_function_by_file('audit',
                                                 'trigger/dbf_cofk_union_audit_any_v2.sql',
                                                 'trigger/dbf_cofk_union_audit_any.sql'),
    ]
