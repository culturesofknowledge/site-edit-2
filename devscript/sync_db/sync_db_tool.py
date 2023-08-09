from pathlib import Path
import collections
from typing import Iterable
import re


class ColorCodes:
    grey = '\u001b[38;5;250m'
    black = '\u001b[38;5;232m'
    bg_blue = '\u001b[44m'
    bg_yellow = '\u001b[43m'
    bg_red = '\u001b[41m'
    bg_purple = '\u001b[45m'
    reset = "\u001b[0m"


def find_statements(sql) -> Iterable[str]:
    cur_idx = -1
    start_cut_idx = None
    while cur_idx < len(sql):
        cur_char = sql[cur_idx]
        if start_cut_idx is None:
            if not cur_char.isspace():
                start_cut_idx = cur_idx
        else:
            if cur_char == ';':
                yield sql[start_cut_idx: cur_idx + 1]
                start_cut_idx = None

        cur_idx += 1


def to_oneline(s):
    return s.replace('\n', '')


class to_color:
    def __init__(self, color):
        self.color = color

    def __enter__(self):
        print(self.color)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(ColorCodes.reset)


def main():
    path = 'sync_db.230615.sql'
    sql = Path(path).read_text()

    comments = re.findall(r'\s*--.+', sql)
    comments = [c.strip() for c in comments]
    for c in set(comments):
        sql = sql.replace(c, '')

    statements = find_statements(sql)
    statements = (s.strip() for s in statements)

    sql_maps = collections.defaultdict(list)
    other_statements = []
    for s in statements:
        if s.startswith('drop table'):
            sql_maps['added_tables'].append(re.findall(r'drop table (\w+);', s)[0])
        elif s.startswith('create table'):
            sql_maps['deleted_tables'].append(re.findall(r'create table (\w+)', s)[0])
        elif 'set default nextval(' in s:
            sql_maps['seq'].append(to_oneline(s))
        elif 'set default "current_user"()' in s:
            # new system not support current_user()
            sql_maps['current_user'].append(to_oneline(s))
        elif 'create trigger' in s:
            sql_maps['missed trigger'].append(s)
        elif 'drop index ' in s:
            sql_maps['added_index'].append(to_oneline(s))
        elif result := re.findall(r'alter table (\w+).+drop column (\w+);', s, re.DOTALL):
            sql_maps['added_column'].append(result)
        elif 'owner to ' in s:
            sql_maps['owner_to'].append(to_oneline(s))
        elif 'add primary key ' in s:
            # django not support composite primary
            sql_maps['missed primary key'].append(s)
        elif 'type timestamp using ' in s:
            sql_maps['change timestamp type'].append(to_oneline(s))
        elif s.startswith('comment on table '):
            sql_maps['comment on table'].append(s)
        elif 'create index ' in s:
            sql_maps['missed index'].append(s)
        elif 'add constraint' in s:
            if re.search(r'add constraint .+ foreign key ', s, re.DOTALL):
                key = 'missed_foreign_key'
            else:
                key = 'missed_constraint'
            sql_maps[key].append(s)
        elif 'drop constraint ' in s:
            sql_maps['added constraint'].append(s)


        elif re.search(r'add constraint .+ foreign key ', s, re.DOTALL):
            sql_maps['missed_foreign_key'].append(s)
        elif re.search(r'alter column \w+ type', s):
            sql_maps['mismatch column type'].append(s)
        elif 'set default now()' in s:
            sql_maps['missing default now()'].append(s)
        elif 'set not null' in s:
            sql_maps['missing not null'].append(s)
        else:
            other_statements.append(s)

    info_keys = ['added_tables', 'deleted_tables', 'added_column',
                 'owner_to', 'missed primary key', 'change timestamp type',
                 'seq', 'current_user', 'added_index', 'missed_constraint',
                 'comment on table', 'missed trigger', 'missed index', 'added constraint']
    info_keys = (i for i in info_keys if i in sql_maps)
    with to_color('\u001b[46;30m'):
        for k in info_keys:
            values = sql_maps.pop(k)
            values = sorted(values)
            print_key_values(k, values)

    for k, values in sql_maps.items():
        print_key_values(k, values)

    print('--------------------- other statements')
    for s in other_statements:
        print('-------------------')
        print(s)


def print_key_values(k, values):
    print(f'--------------------- {k}')
    for n in values:
        print(n)
    print()


if __name__ == '__main__':
    main()
