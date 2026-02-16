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

# Example: Get a work and print it
work = dt.get_work_from_iwork_id(12345)
print(work)

# Example: Create a relationship
dt.create_relationship_created(person_id='person-1', work_id='work-1')

# Example: Commit changes
dt.commit_changes(commit=True)
```

## Shell Usage

You can also use the tweaker directly from the command line to start an interactive shell:

```bash
# Start interactive shell using Django settings
python -m tweaker --shell

# Connect directly using a database URL
python -m tweaker --shell --url postgresql://user:pass@host:5432/dbname
```

## Commands Reference

The following methods are available on the `dt` (DatabaseTweaker) instance.

### GET Methods
Retrieve a single row as a dictionary (or `None` if not found).

- `get_work_from_iwork_id(iwork_id: int)`
- `get_work_from_work_id(work_id: str)`
- `get_person_from_iperson_id(iperson_id: int)`
- `get_person_from_person_id(person_id: str)`
- `get_location_from_location_id(location_id: int)`
- `get_institution_from_institution_id(institution_id: int)`
- `get_manifestation_from_manifestation_id(manifestation_id: str)`
- `get_resource_from_resource_id(resource_id: int)`
- `get_image_from_image_id(image_id: int)`
- `get_comment_from_comment_id(comment_id: int)`

### CREATE Methods
Insert new records and return the primary key or the new record ID.

- `create_work(work_id_end, ...)`
- `create_person_or_organisation(primary_name, ...)`
- `create_location(element_4_eg_city, element_6_eg_country, ...)`
- `create_manifestation(manifestation_id, manifestation_type, ...)`
- `create_comment(comment_text)`
- `create_resource(name, url, description)`
- `create_image(filename, display_order, ...)`

### UPDATE Methods
Update existing records using a dictionary of field changes.

- `update_work(work_id, field_updates: dict)`
- `update_work_from_iwork(iwork_id, field_updates: dict)`
- `update_person(person_id, field_updates: dict)`
- `update_person_from_iperson(iperson_id, field_updates: dict)`
- `update_location(location_id, field_updates: dict)`
- `update_institution(institution_id, field_updates: dict)`
- `update_manifestation(manifestation_id, field_updates: dict)`
- `update_comment(comment_id, field_updates: dict)`
- `update_resource(resource_id, field_updates: dict)`
- `update_image(image_id, field_updates: dict)`

### Relationship Methods (Mapping Tables)
Create links between entities.

- `create_work_person_map(work_id, person_id, relationship_type)`
- `create_work_location_map(work_id, location_id, relationship_type)`
- `create_work_comment_map(work_id, comment_id, relationship_type)`
- `create_work_resource_map(work_id, resource_id)`
- `create_work_work_map(work_from_id, work_to_id, relationship_type)`
- `create_person_comment_map(person_id, comment_id, ...)`
- `create_person_resource_map(person_id, resource_id)`
- `create_person_location_map(person_id, location_id, relationship_type)`
- `create_manif_comment_map(manifestation_id, comment_id, ...)`
- `create_manif_inst_map(manifestation_id, institution_id, ...)`

#### Convenience Relationship Methods
- `create_relationship_created(person_id, work_id)`
- `create_relationship_addressed_to(work_id, person_id)`
- `create_relationship_mentions(work_id, person_id)`
- `create_relationship_was_sent_from(work_id, location_id)`
- `create_relationship_was_sent_to(work_id, location_id)`
- `create_relationship_work_reply_to(work_reply_id, work_id)`
- (and many others for specific types like `signed`, `sent`, `intended_for`, `born_in`, `died_at`, etc.)

### Querying Mapping Tables
Retrieve lists of relationship dictionaries.

- `get_work_person_maps(work_id=, person_id=, relationship_type=)`
- `get_work_location_maps(work_id=, location_id=, relationship_type=)`
- `get_work_comment_maps(work_id=, comment_id=, relationship_type=)`
- `get_work_resource_maps(work_id=, resource_id=)`
- `get_work_work_maps(work_from_id=, work_to_id=, relationship_type=)`

### DELETE Methods
- `delete_work_via_work_id(work_id)`
- `delete_work_via_iwork_id(iwork_id)`
- `delete_manifestation_via_manifestation_id(manifestation_id)`
- `delete_comment_via_comment_id(comment_id)`
- `delete_resource_via_resource_id(resource_id)`
- `delete_work_person_map(recref_id)`
- `delete_work_location_map(recref_id)`
- (and other mapping-specific delete methods)

### Raw SQL and Transactions
- `execute_raw(sql, params=None)` — returns a list of dictionaries
- `execute_scalar(sql, params=None)` — returns a single value
- `commit_changes(commit=False)` — use `commit=True` to persist changes to the DB
- `print_audit()` — show what changes are pending or were just made

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
