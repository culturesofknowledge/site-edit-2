# Tweaker

Database manipulation tool for CofK/EMLO. Used by `tweak_*` batch scripts to create, update, and delete works, people, locations, manifestations, comments, resources, and their relationships.

## Old vs New

The old tweaker lives at `site-edit/emlo-edit-php-helper/tweaker`. The new one (this module) is a rewrite for the `site-edit-2` Django project.

### Database driver

| | Old | New |
|---|---|---|
| **Driver** | psycopg2 (raw SQL via `cursor.mogrify`) | SQLAlchemy Core |
| **Connection** | `psycopg2.connect(connstring)` | `create_engine(url)` with connection pooling |
| **Queries** | Hand-written SQL strings with `%s` placeholders | `select()`, `insert()`, `update()`, `delete()` expressions |
| **Table metadata** | Hardcoded column lists in every method | Reflected from DB via `MetaData` / `Table(autoload_with=)` |

### Relationships

This is the biggest architectural change.

| | Old | New |
|---|---|---|
| **Storage** | Single `cofk_union_relationship` table with `left_table_name`, `left_id_value`, `right_table_name`, `right_id_value` columns | Dedicated mapping tables per entity pair (`cofk_work_person_map`, `cofk_work_location_map`, `cofk_person_location_map`, etc.) |
| **Create** | `create_relationship(left_name, left_id, rel_type, right_name, right_id)` | `create_work_person_map(work_id, person_id, rel_type)` and similar typed methods |
| **Query** | `get_relationships(id_from, table_from, table_to)` — generic but required post-processing to figure out left vs right | `get_work_person_maps(work_id=, person_id=, relationship_type=)` — typed, filterable |
| **Delete** | `delete_relationship_via_relationship_id()` | `delete_work_person_map(recref_id)` and similar per-table methods |
| **Validation** | None — any string accepted as `relationship_type` | `VALID_RELATIONSHIP_TYPES` dict rejects invalid types with `InvalidRelationshipTypeError` |
| **Duplicates** | Silently created | Check-before-insert raises `DuplicateRelationshipError` (bypassable with `skip_duplicate_check=True`) |

The convenience methods (`create_relationship_created`, `create_relationship_was_sent_from`, etc.) have identical signatures in both versions so `tweak_*` scripts need minimal changes.

### Error handling

| | Old | New |
|---|---|---|
| **Connection failure** | `sys.exit(1)` | Raises `SQLAlchemyError` |
| **DB not connected** | Raises `psycopg2.DatabaseError` | Raises `SQLAlchemyError` |
| **`execute_raw` errors** | N/A | Catches only `ResourceClosedError` (non-SELECT); real DB errors propagate |
| **`execute_scalar` errors** | N/A | Re-raises `SQLAlchemyError` with the SQL statement in the message |
| **Custom exceptions** | None | `TweakerError`, `DuplicateRelationshipError`, `InvalidRelationshipTypeError` |

### Features only in the new version

- `from_django_settings()` — creates a tweaker using Django's `DATABASES` config
- `execute_raw(sql)` / `execute_scalar(sql)` — run arbitrary SQL
- `add_language_to_work()` / `add_language_to_manifestation()` — idempotent via `ON CONFLICT DO NOTHING`
- `create_manifestation()` with full field support (the old version only supported 4 fields)
- `create_person_or_organisation()` with full birth/death/flourished date ranges and calendar fields
- Type annotations throughout
- Mapping table query methods (`get_work_person_maps`, `get_work_location_maps`, etc.)
- `connect_to_postgres()` kept as a backwards-compatibility shim that parses the old psycopg2 connection string format

### Features only in the old version

- `get_relationships()` — generic relationship query (not needed with mapping tables)
- `delete_relationship_via_relationship_id()` — operates on old relationship table
- `load_schema()` / `convert_field_type()` — JSON schema-based type conversion
- `csv_unicode.py`, `uploader.py`, `automater.py` — companion modules not ported

## Usage

```python
from tweaker import DatabaseTweaker

# From Django settings
dt = DatabaseTweaker.from_django_settings()

# Direct connection
dt = DatabaseTweaker.tweaker_from_connection(dbname, host, port, user, password)

# Direct URL
dt = DatabaseTweaker("postgresql://user:pass@host:5432/dbname")
```

## Tests

```bash
# All tweaker tests (unit + integration) in Docker
docker compose -f docker-compose.yml -f docker-compose-dev.yml exec pycharm-py \
    python manage.py test tweaker -v 2

# Unit tests only (no DB needed)
python -m tweaker.tests
```

Test layout:
- `tweaker/tests.py` — unit tests, mocked tests (no DB required), plus Django integration tests
- `tweaker/test/test_tweak_compatibility.py` — integration tests verifying `tweak_*` script patterns, duplicate detection, delete methods, error paths
