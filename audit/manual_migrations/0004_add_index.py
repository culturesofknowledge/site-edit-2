from django.db import migrations

from sharedlib.djangolib import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('audit', '0003_sync_old_schema'),
    ]
    operations = [
        migrations_utils.create_operation_add_index('cofk_union_audit_literal_change_timestamp', 'cofk_union_audit_literal',
                                                    ['change_timestamp desc']),
        migrations_utils.create_operation_add_index('cofk_union_audit_literal_change_user', 'cofk_union_audit_literal',
                                                    ['change_user']),
    ]
