from typing import Iterable

from django.db import migrations
from django.db.migrations.operations.base import Operation


def _create_trigger_name(table_name, action):
    return f'{table_name}_trg_audit_{get_action_name(action)}'


def get_action_name(action):
    action_map = {
        'delete': 'del',
        'insert': 'ins',
        'update': 'upd',
    }
    if action_name := action_map.get(action):
        return action_name
    else:
        raise ValueError(f'unknown action -- {action}')


def create_audit_trigger_sql(table_name, action):
    action_name = get_action_name(action)
    when = 'before' if 'delete' else 'after'
    return f"""
    create trigger {table_name}_trg_audit_{action_name}
    {when} {action}
    on {table_name}
    for each row
    execute procedure dbf_cofk_union_audit_any();
    """


def create_audit_trigger_list(table_name) -> Iterable[Operation]:
    action_list = ['delete',
                   'insert',
                   'update']
    for action in action_list:
        trigger_name = _create_trigger_name(table_name, action)
        sql = create_audit_trigger_sql(table_name, action)
        yield migrations.RunSQL(
            sql, f'drop trigger {trigger_name} on {table_name}'
        )
