# EMLO Site Edit-2
This repository is a re-boot of the software behind the 
[Early Modern Letters Online (EMLO)](http://emlo.bodleian.ox.ac.uk/home) project for the 
[Bodleian Libraries](https://www.bodleian.ox.ac.uk/home) of the University of Oxford. 

More precisely this repository holds a new front-end design of the old one that can be found 
[here](https://github.com/culturesofknowledge/site-edit).

Project resides [here](https://github.com/culturesofknowledge/emlo-project/projects) and a list of relevant documents
can be found [here](https://github.com/culturesofknowledge/emlo-project/wiki/List-of-Documents).

The previous development approach was based on a modular, decoupled (almost) services like approach we are now
going for a more monolithic style approach.

Dependencies (see `requirements.txt`):
* Postgres
* Django 4.0.4
* django-sass-processor -- https://github.com/jrief/django-sass-processor

How to run all unitest with docker 
------------------------------------
```shell
docker-compose -f $EMLO_CODE_HOME/docker-compose.yml -f $EMLO_CODE_HOME/docker-compose-pycharm.yml -f $EMLO_CODE_HOME/docker-compose-unittest.yml up pycharm-py
```

How to use data migration tool
--------------------------------------

```shell
python3 manage.py data_migration -d ouls -p password -u postgres -o 172.17.0.1 -t 15432
```
* all input parameter is for connecting to old database (old db name, old password, old db host....  )

### if you need to use your own *settings* you can use --settings
```shell
python3 manage.py data_migration --settings=siteedit2.settings.local_dev -d ouls -p password -u postgres -o 172.17.0.1 -t 15432
```

How to create superuser 
----------------------------------
```shell
python3 manage.py createsuperuser
```


# Changes to database schema

Because of EMLO Edit's interdependence with EMLO Collect and EMLO Front end it has been a major requirement to
leave the database schema as unchanged as possible.

The changes that have been made were due either to the older version being incompatible with Django or to increase
efficiency. The previous database schema had several views which are not used in the new database schema.



| Table name                                                                                                                                                                                                                                                                                                                                                                                                                    | Action                                            | Purpose                                             | Comment                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cofk_collect_institution`, `cofk_collect_location`, `cofk_collect_manifestation`, `cofk_collect_person`, `cofk_collect_work`                                                                                                                                                                                                                                                                                                 | Primary key column added                          | Transient data for reviews                          | 5 main entity collect tables. See discussion below under Collect tables changes                                                                                                                                                                                                                                                                                                            |
| `cofk_collect_addressee_of_work`, `cofk_collect_author_of_work`, `cofk_collect_destination_of_work`, `cofk_collect_institution_resource`, `cofk_collect_location_resource`, `cofk_collect_occupation_of_person`, `cofk_collect_origin_of_work`, `cofk_collect_person_mentioned_in_work`, `cofk_collect_person_resource`, `cofk_collect_place_mentioned_in_work`, `cofk_collect_subject_of_work`, `cofk_collect_work_resource` | Main entity column now references new primary key | Transient data for reviews                          | 12 secondary relationship tables. See discussion below under Collect tables changes                                                                                                                                                                                                                                                                                                        |
| `cofk_collect_image_of_manif`                                                                                                                                                                                                                                                                                                                                                                                                 | Data migrated                                     | Transient data for reviews                          | A secondary table seemingly not used. All `iwork_ids` are null and all `image_filename` values are of the format "012r" or "012v". There are 25,868 records in this table. Because there are no linked works in this table there is no unique constraint set.                                                                                                                              |
| `cofk_collect_work_summary`                                                                                                                                                                                                                                                                                                                                                                                                   | Dropped                                           | Transient data for reviews                          | In the old database there is the function `dbf_cofk_collect_write_work_summary` which is called in `upload_import2Postgres.php` serving a compatible function to `cofk_union_queryable_work` and `cofk_union_person_summary`. Note that this is only called via EMLO Edit which explains the difference of records between CofkCollectwork (330.361) and CofkCollectWorkSummary (288.498). |
| `cofk_union_queryable_work`, `cofk_union_person_summary`                                                                                                                                                                                                                                                                                                                                                                      | Dropped                                           | To make entities related to works/people searchable | Related entities made searchable using joins                                                                                                                                                                                                                                                                                                                                               |
| `pro_activity`, `pro_activity_relation`, `pro_assertion`, `pro_ingest_map_v2`, `pro_ingest_v8`, `pro_ingest_v8_toreview`, `pro_location`, `pro_people_check`, `pro_primary_person`, `pro_relationship`, `pro_role_in_activity`, `pro_textual_source`                                                                                                                                                                          | Dropped                                           | To hold information on prosopography                |                                                                                                                                                                                                                                                                                                                                                                                            |
| `cofk_collect_tool_user`, `cofk_collect_tool_session`                                                                                                                                                                                                                                                                                                                                                                         | Table created but data not migrated               |                                                     | User table only holds one row, session table is empty.                                                                                                                                                                                                                                                                                                                                     |
| `cofk_union_nationality`                                                                                                                                                                                                                                                                                                                                                                                                      | Table created                                     |                                                     | Table holds no data in original schema. No references in new codebase. There is `nationality.php` and relationship type `RELTYPE_PERSON_MEMBER_OF_NATIONALITY` in old codebase.                                                                                                                                                                                                            |    
| `cofk_union_speed_entry_text`                                                                                                                                                                                                                                                                                                                                                                                                 | Dropped                                           | Helper prompt when editing resources                | Old table holds 19 rows. Replaced with JS prompts in forms.                                                                                                                                                                                                                                                                                                                                |
| `cofk_help_options`, `cofk_help_pages`                                                                                                                                                                                                                                                                                                                                                                                        | Dropped                                           |                                                     | Both tables are empty and not referenced in old codebase.                                                                                                                                                                                                                                                                                                                                  |
| `cofk_menu`                                                                                                                                                                                                                                                                                                                                                                                                                   | Dropped                                           | Internal routing table                              | Hierarchical routing table with 182 rows.                                                                                                                                                                                                                                                                                                                                                  |
| `cofk_reports`, `cofk_report_groups`, `cofk_report_outputs`                                                                                                                                                                                                                                                                                                                                                                   | Dropped                                           |                                                     | All three tables empty.                                                                                                                                                                                                                                                                                                                                                                    |
| `cofk_union_relationship`                                                                                                                                                                                                                                                                                                                                                                                                     | Dropped                                           | Mapping relationships between entities              | This table had ~1.5 million rows. It has been broken down into dedicated relationship tables managed by Django such as `cofk_institution_resource_map` that links institutions to resources.                                                                                                                                                                                               |

## Collect table changes
The Collect tables used composite primary keys extensively, combining the upload id and the entity id.
Django does not support composite primary keys (see [overview](https://code.djangoproject.com/wiki/MultipleColumnPrimaryKeys))
the solution has therefore been to use the collect entity keys as foreign keys to the new main entity primary keys. For instance:

```sql
CREATE TABLE IF NOT EXISTS public.cofk_collect_location
(
    upload_id integer NOT NULL,
    location_id integer NOT NULL,
    ...
CONSTRAINT cofk_collect_location_pkey PRIMARY KEY (upload_id, location_id),
```

becomes

```sql
CREATE TABLE IF NOT EXISTS public.cofk_collect_location
(
    id bigint NOT NULL DEFAULT nextval('cofk_collect_location_id_seq'::regclass),
    upload_id integer NOT NULL,
    location_id integer NOT NULL,
    ...
CONSTRAINT cofk_collect_location_pkey PRIMARY KEY (id),
CONSTRAINT cofk_collect_location_upload_id_location_id_50c243da_uniq UNIQUE (upload_id, location_id),
```

The secondary Collect tables that hold information about relationship types can no longer link to parent tables via
composite keys and instead have to refer to the single primary key in the collect table, they go from:

```sql
CREATE TABLE IF NOT EXISTS public.cofk_collect_destination_of_work
(
    upload_id integer NOT NULL,
    destination_id integer NOT NULL,
    location_id integer NOT NULL,
    iwork_id integer NOT NULL,
    ...
CONSTRAINT cofk_collect_destination_of_work_pkey PRIMARY KEY (upload_id, iwork_id, destination_id),
```

to 

```sql
CREATE TABLE IF NOT EXISTS public.cofk_collect_destination_of_work
(
    id bigint NOT NULL DEFAULT nextval('cofk_collect_destination_of_work_id_seq'::regclass),
    destination_id integer NOT NULL,
    location_id bigint NOT NULL,
    upload_id integer NOT NULL,
CONSTRAINT cofk_collect_destination_of_work_pkey PRIMARY KEY (id),
CONSTRAINT cofk_collect_destination_upload_id_iwork_id_desti_d398f1ac_uniq UNIQUE (upload_id, iwork_id, destination_id),
```

with `upload_id`, `iwork_id` and `location_id` being foreign keys.

### Implications for EMLO Collect

EMLO Collect code inserts directly into the Postgres tables and this does not affect the main entity tables as they only
have an added id sequence value.

For the secondary relationship tables however the changes mean that the `*entity*_id` in the secondary table now refers
to the new primary key of the new entity table.