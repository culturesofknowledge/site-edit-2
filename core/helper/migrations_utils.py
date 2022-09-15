from django.db import migrations
from django.db.migrations.operations.base import Operation


def create_operation_default_value(table_name, col_name,
                                   default_val="'__unknown_user'") -> Operation:
    return migrations.RunSQL(
        (f"alter table {table_name} "
         f" alter column {col_name} "
         f" set default {default_val} "),

        (f'alter table {table_name} '
         f' alter column {col_name} '
         ' drop default '),
    )


def create_default_change_user_timestamp(table_name) -> list[Operation]:
    return [
        create_operation_default_value(table_name, 'change_user',
                                       default_val="'__unknown_user'"),
        create_operation_default_value(table_name, 'change_timestamp',
                                       default_val="now()"),
    ]


def create_default_empty(table_name, col_names: list[str]) -> list[Operation]:
    return [
        create_operation_default_value(table_name, col_name, default_val="''")
        for col_name in col_names
    ]


def create_operation_seq(seq_name, init_val=1) -> Operation:
    return migrations.RunSQL(
        f"CREATE SEQUENCE {seq_name} start with {init_val} ",
        f"DROP SEQUENCE {seq_name}",
    )
