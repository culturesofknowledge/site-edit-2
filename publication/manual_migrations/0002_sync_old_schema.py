from django.db import migrations

from core.helper import migrations_utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('publication', '0001_initial'),
        ('core', '0002_basic_db_settings'),
    ]
    operations = [
        migrations_utils.create_operation_default_value('cofk_union_publication', 'publication_details', "''"),
        migrations_utils.create_operation_default_value('cofk_union_publication', 'change_timestamp', 'now()'),
        migrations_utils.create_operation_default_value('cofk_union_publication', 'abbrev', "''"),
    ]
