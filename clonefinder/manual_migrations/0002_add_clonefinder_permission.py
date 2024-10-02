from django.db import migrations

from core import constant

role_name = constant.ROLE_SUPER
new_permissions = [constant.PM_CLONEFINDER_WORK, constant.PM_CLONEFINDER_PERSON, constant.PM_CLONEFINDER_LOCATION,
                   constant.PM_CLONEFINDER_INST]


def add_permission_to_group(apps, schema_editor):
    from core.helper import migrations_serv
    migrations_serv.add_permission_to_group(role_name, new_permissions)


def remove_permission_from_group(apps, schema_editor):
    from core.helper import migrations_serv
    migrations_serv.remove_permission_from_group(role_name, new_permissions)


class Migration(migrations.Migration):
    dependencies = [
        ('clonefinder', '0001_initial'),
        ('work', '0013_alter_cofkunionwork_options'),
        ('location', '0008_alter_cofkunionlocation_options'),
        ('person', '0013_alter_cofkunionperson_options'),
        ('institution', '0006_alter_cofkunioninstitution_options'),

    ]

    operations = [
        migrations.RunPython(add_permission_to_group, reverse_code=remove_permission_from_group),
    ]
