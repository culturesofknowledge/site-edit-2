from django.db.migrations.operations.base import Operation

from cllib_django import migrations_utils


def create_default_change_user_timestamp(table_name) -> list[Operation]:
    return [
        migrations_utils.create_operation_default_value(table_name, 'change_user',
                                                        default_val="'__unknown_user'"),
        migrations_utils.create_operation_default_value(table_name, 'change_timestamp',
                                                        default_val="now()"),
    ]
