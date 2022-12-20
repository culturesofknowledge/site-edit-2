from pathlib import Path
import collections
from typing import Iterable
import re


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


def main():
    path = 'sync_db.221220.sql'
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
            sql_maps['seq'].append(s.replace('\n', ''))
        elif 'type timestamp using ' in s:
            sql_maps['change timestamp type'].append(s.replace('\n', ''))
        elif 'set default "current_user"()' in s:
            sql_maps['current_user'].append(s.replace('\n', ''))
        elif 'drop index ' in s:
            sql_maps['added_index'].append(s.replace('\n', ''))
        elif result := re.findall(r'alter table (\w+).+drop column (\w+);', s, re.DOTALL):
            sql_maps['added_column'].append(result)
        elif 'add constraint ' in s:
            sql_maps['missed_constraint'].append(s)
        elif 'owner to ' in s:
            sql_maps['owner_to'].append(s)
        elif 'add primary key ' in s:
            sql_maps['missed primary key'].append(s)
        elif 'create index ' in s:
            sql_maps['missed index'].append(s)
        elif 'drop constraint ' in s:
            sql_maps['added constraint'].append(s)
        elif 'create trigger' in s:
            sql_maps['missed trigger'].append(s)
        elif s.startswith('comment on table '):
            sql_maps['comment on table'].append(s)
        elif re.search(r'alter column \w+ type', s):
            sql_maps['mismatch column type'].append(s)
        elif 'set default now()' in s:
            sql_maps['missing default now()'].append(s)
        elif 'set not null' in s:
            sql_maps['missing not null'].append(s)
        else:
            other_statements.append(s)

    for k, values in sql_maps.items():
        print(f'--------------------- {k}')
        for n in values:
            print(n)

    print('--------------------- other statements')
    for s in other_statements:
        print('-------------------')
        print(s)


if __name__ == '__main__':
    main()
