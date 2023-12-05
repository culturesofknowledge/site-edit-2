from django.db import migrations

from cllib_django import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0004_sync_old_schema'),
    ]
    operations = [
        migrations_utils.create_operation_seq('iso_639_language_codes_id_seq')
    ]
