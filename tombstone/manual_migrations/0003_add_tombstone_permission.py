from django.db import migrations

from core import constant

role_name = constant.ROLE_SUPER
new_permissions = [constant.PM_TOMBSTONE_WORK, constant.PM_TOMBSTONE_PERSON, constant.PM_TOMBSTONE_LOCATION,
                   constant.PM_TOMBSTONE_INST]


def add_permission_to_group(apps, schema_editor):
    from core.helper import migrations_serv
    migrations_serv.add_permission_to_group(role_name, new_permissions)


def remove_permission_from_group(apps, schema_editor):
    from core.helper import migrations_serv
    migrations_serv.remove_permission_from_group(role_name, new_permissions)


class Migration(migrations.Migration):
    dependencies = [
        ('tombstone', '0002_tombstonerequest_sql_params'),
        ('work', '0012_alter_cofkunionwork_options'),
        ('location', '0007_alter_cofkunionlocation_options'),
        ('person', '0012_alter_cofkunionperson_options'),
        ('institution', '0005_alter_cofkunioninstitution_options'),

    ]

    operations = [
        migrations.RunPython(add_permission_to_group, reverse_code=remove_permission_from_group),
    ]
