from django.db.migrations.operations.base import Operation

from cllib_django import migrations_utils


def create_default_change_user_timestamp(table_name) -> list[Operation]:
    return [
        migrations_utils.create_operation_default_value(table_name, 'change_user',
                                                        default_val="'__unknown_user'"),
        migrations_utils.create_operation_default_value(table_name, 'change_timestamp',
                                                        default_val="now()"),
    ]


def add_permission_to_group(role_name, new_permissions):
    from core.helper import perm_serv
    from django.contrib.auth.models import Group

    group = Group.objects.get(name=role_name)
    for perm_code in new_permissions:
        permission = perm_serv.get_perm_by_full_name(perm_code)
        group.permissions.add(permission)


def remove_permission_from_group(role_name, new_permissions):
    from core.helper import perm_serv
    from django.contrib.auth.models import Group

    group = Group.objects.get(name=role_name)
    for perm_code in new_permissions:
        permission = perm_serv.get_perm_by_full_name(perm_code)
        group.permissions.remove(permission)
